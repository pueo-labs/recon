# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportMissingParameterType=none, reportPrivateUsage=none, reportUnknownArgumentType=none
# pyright: reportUnknownMemberType=none, reportUnknownParameterType=none, reportUnknownVariableType=none
"""Hand-computed unit anchors for the inference-core math helpers.

The 2026-06 mutation baseline (validation/mutation-gate.md) showed the
surviving mutants clustering in helpers the behavior suites exercise
only indirectly: the credible-interval arithmetic, the CAL14 declarative
evidence counting, the evidence
influence ranking, the correlation-group reduction, the priors-override
loader, and the TenantInfo adapters. Each test here pins one of those
helpers to values computed by hand (or to a documented approximation
band), so a subtle arithmetic change fails a named assertion instead of
slipping through. This file runs first in the mutation kill-set
(mutation.toml); keep it fast and dependency-light.

The 2026-07 collection-aware pass adds exact contracts for probability
boundaries, neutral marginal fallbacks, whole-channel masking, and adapter
extraction. These distinguish an unavailable observation from informative
absence without expanding the accepted mathematical input domains.
"""

from __future__ import annotations

import math
from types import SimpleNamespace

import pytest

from recon_tool.bayesian import (
    _CONFLICT_N_EFF_PENALTY,
    BayesianNetwork,
    CalibrationSettings,
    _binding_llr,
    _conflict_provenance,
    _contributing_evidence,
    _declarative_evidence_count,
    _Evidence,
    _factor_is_probabilities,
    _factor_is_strictly_positive,
    _marginal_in_unit_range,
    _Node,
    _query_marginal,
    _rank_evidence,
    collection_masked_units,
    infer,
    infer_from_tenant_info,
    load_network,
    load_priors_override,
    signals_from_tenant_info,
)
from recon_tool.bayesian_interval import credible_interval as _credible_interval
from recon_tool.bayesian_interval import interval_is_ordered as _interval_is_ordered
from recon_tool.constants import SVC_SPF_STRICT


def _ev(name: str, lp: float, la: float, group: str | None = None, kind: str = "slug") -> _Evidence:
    return _Evidence(kind=kind, name=name, likelihood_present=lp, likelihood_absent=la, group=group)


# Deterministic rich-evidence input shared by the output-field anchors: fires
# bindings across hideable and declarative nodes so posteriors, intervals,
# entropy reductions, and unit counterfactuals all carry pinnable values.
_RICH_SLUGS: list[str] = []
_RICH_SIGNALS = [
    "m365_tenant_observed",
    "okta_idp_observed",
    "cdn_cname_observed",
    "dmarc_reject",
    "spf_strict",
    "federated_sso_hub",
]


# ── _credible_interval ─────────────────────────────────────────────────


class TestCredibleInterval:
    def test_default_width_hand_computed(self) -> None:
        # p=0.5, n_eff=4 gives Beta(2,2). Its CDF is 3x^2 - 2x^3.
        low, high = _credible_interval(0.5, 4.0, 0.80)
        assert abs(low - 0.19580010565909173) < 1e-12
        assert abs(high - 0.8041998943409083) < 1e-12

    def test_95_branch_hand_computed(self) -> None:
        # Same Beta(2,2) closed form at the 0.025 and 0.975 quantiles.
        low, high = _credible_interval(0.5, 4.0, 0.95)
        assert abs(low - 0.09429932405024608) < 1e-12
        assert abs(high - 0.9057006759497541) < 1e-12

    def test_width_narrows_with_n_eff(self) -> None:
        low4, high4 = _credible_interval(0.5, 4.0, 0.80)
        low16, high16 = _credible_interval(0.5, 16.0, 0.80)
        assert (high16 - low16) < (high4 - low4)

    def test_general_width_uses_exact_quantile(self) -> None:
        # Central 50 percent for Beta(2,2), CDF closed form.
        low, high = _credible_interval(0.5, 4.0, 0.5)
        assert abs(low - 0.3263518223330697) < 1e-12
        assert abs(high - 0.6736481776669303) < 1e-12

    def test_clamps_to_unit_interval(self) -> None:
        low, high = _credible_interval(0.02, 4.0, 0.80)
        assert low == 0.0
        assert abs(high - (0.02 + 1.2816 * math.sqrt(0.02 * 0.98 / 4.0))) < 1e-9
        assert 1.0 - _credible_interval(0.98, 4.0, 0.80)[1] < 1e-12

    def test_nonpositive_n_eff_is_vacuous(self) -> None:
        assert _credible_interval(0.7, 0.0) == (0.0, 1.0)
        assert _credible_interval(0.7, -1.0) == (0.0, 1.0)


# ── CAL14 declarative evidence counting ────────────────────────────────


class TestDeclarativeEvidenceCount:
    def _node(self, evidence: tuple[_Evidence, ...], group_absence: tuple[tuple[str, float, float], ...]) -> _Node:
        return _Node(
            name="n",
            description="d",
            parents=(),
            prior=0.5,
            cpt={},
            evidence=evidence,
            missingness="declarative",
            group_absence=group_absence,
        )

    def test_counts_fired_strong_absent_and_informative_groups(self) -> None:
        # Fired A contributes one unit. Every applied non-neutral absence also
        # counts: B, weak C, group g, and weak group h. Group g still counts
        # only once for its two mutually exclusive members. Total: 5.
        node = self._node(
            evidence=(
                _ev("a", 0.9, 0.1),
                _ev("b", 0.9, 0.3),
                _ev("c", 0.5, 0.55),
                _ev("g1", 0.8, 0.2, group="g"),
                _ev("g2", 0.7, 0.2, group="g"),
                _ev("h1", 0.6, 0.3, group="h"),
            ),
            group_absence=(("g", 0.2, 0.8), ("h", 0.5, 0.55)),
        )
        fired = [node.evidence[0]]
        assert _declarative_evidence_count(node, fired) == 5

    @pytest.mark.parametrize(
        ("slugs", "signals", "expected_fired", "expected_units", "posterior_odds"),
        [
            # Both names appear on one channel. Only its declared binding fires.
            # The prior odds are one. Multiply the fired and absent likelihood ratios.
            (
                ["member", "ticket"],
                [],
                "slug:member",
                {("shared", "group", "fired"), ("ticket", "signal", "absent")},
                (0.75 / 0.25) * (0.5 / 0.25),
            ),
            (
                [],
                ["member", "ticket"],
                "signal:ticket",
                {("shared", "group", "absent"), ("ticket", "signal", "fired")},
                (0.25 / 0.75) * (0.5 / 0.75),
            ),
        ],
        ids=["slug-observed", "signal-observed"],
    )
    def test_mixed_declarations_keep_counts_and_provenance_by_kind(
        self,
        slugs: list[str],
        signals: list[str],
        expected_fired: str,
        expected_units: set[tuple[str, str, str]],
        posterior_odds: float,
    ) -> None:
        node = self._node(
            evidence=(
                _ev("member", 0.75, 0.25, group="shared"),
                _ev("ticket", 0.5, 0.75, kind="signal"),
                _ev("neutral", 0.5, 0.5),
            ),
            group_absence=(("shared", 0.25, 0.75),),
        )
        post = infer(BayesianNetwork(1, (node,)), slugs, signals, priors_override={}).posteriors[0]

        assert post.evidence_used == (expected_fired,)
        assert {(cf.unit, cf.kind, cf.observed) for cf in post.unit_counterfactuals} == expected_units
        assert post.absence_informative
        assert post.n_eff == 6.0  # Baseline four plus one fired and one informative absent unit.
        assert post.posterior == round(posterior_odds / (1 + posterior_odds), 4)

    def test_fired_group_not_double_counted_as_absent(self) -> None:
        node = self._node(
            evidence=(_ev("g1", 0.8, 0.2, group="g"), _ev("g2", 0.7, 0.2, group="g")),
            group_absence=(("g", 0.2, 0.8),),
        )
        fired = [node.evidence[0]]
        assert _declarative_evidence_count(node, fired) == 1

    def test_absent_group_without_pair_does_not_count(self) -> None:
        node = self._node(
            evidence=(_ev("g1", 0.8, 0.2, group="g"),),
            group_absence=(),
        )
        assert _declarative_evidence_count(node, []) == 0


# ── Correlation-group reduction ────────────────────────────────────────


class TestContributingEvidence:
    def test_group_reduces_to_strongest_member(self) -> None:
        # |LLR|: m1 = log(9) = 2.20, m2 = log(2) = 0.69; m1 wins.
        m1 = _ev("m1", 0.9, 0.1, group="g")
        m2 = _ev("m2", 0.6, 0.3, group="g")
        u1 = _ev("u1", 0.7, 0.4)
        out = _contributing_evidence([m2, m1, u1])
        assert {e.name for e in out} == {"m1", "u1"}

    def test_ungrouped_pass_through(self) -> None:
        evs = [_ev("a", 0.9, 0.1), _ev("b", 0.6, 0.3)]
        assert _contributing_evidence(evs) == evs


# ── Evidence influence ranking ─────────────────────────────────────────


class TestRankEvidence:
    def test_small_valid_likelihoods_keep_their_actual_ratio(self) -> None:
        ranked = _rank_evidence([_ev("tiny", 1e-20, 1e-30), _ev("ordinary", 0.9, 0.1)])
        assert [entry.name for entry in ranked] == ["tiny", "ordinary"]
        assert ranked[0].llr == round(math.log(1e10), 4)
        total = math.log(1e10) + math.log(9)
        assert ranked[0].influence_pct == round(100 * math.log(1e10) / total, 2)

    @pytest.mark.parametrize(("lp", "la"), [(0.5, 5e-324), (5e-324, 0.5)])
    def test_group_selection_and_ranking_stay_finite_at_float_extremes(self, lp: float, la: float) -> None:
        extreme = _ev("extreme", lp, la, group="g")
        ordinary = _ev("ordinary", 0.9, 0.1, group="g")
        expected = math.log(lp) - math.log(la)
        assert math.isfinite(_binding_llr(extreme))
        assert _binding_llr(extreme) == expected
        assert _contributing_evidence([ordinary, extreme]) == [extreme]
        contribution = _rank_evidence([extreme])[0]
        assert contribution.llr == round(expected, 4)
        assert contribution.influence_pct == 100.0

    def test_hand_computed_llr_and_shares(self) -> None:
        # a: log(0.9/0.1) = log 9 = 2.1972; b: log(0.6/0.3) = log 2 =
        # 0.6931. abs_sum = 2.8904, so a carries 76.02% and b 23.98%.
        ranked = _rank_evidence([_ev("b", 0.6, 0.3), _ev("a", 0.9, 0.1)])
        assert [c.name for c in ranked] == ["a", "b"]
        assert ranked[0].llr == round(math.log(9), 4)
        assert ranked[1].llr == round(math.log(2), 4)
        assert ranked[0].influence_pct == 76.02
        assert ranked[1].influence_pct == 23.98

    def test_tie_breaks_on_kind_then_name(self) -> None:
        a = _ev("zzz", 0.9, 0.1, kind="signal")
        b = _ev("aaa", 0.9, 0.1, kind="slug")
        ranked = _rank_evidence([b, a])
        assert [(c.kind, c.name) for c in ranked] == [("signal", "zzz"), ("slug", "aaa")]

    def test_strongest_ranks_first_against_name_order(self) -> None:
        # The strong binding sorts LAST by (kind, name) but FIRST by
        # descending |LLR|. Pinning that the strong one leads kills a
        # sort-key sign flip (``-abs`` -> ``+abs`` / ``not abs``), which a
        # case whose magnitude order matches name order cannot catch.
        strong = _ev("zzz_strong", 0.95, 0.05)
        weak = _ev("aaa_weak", 0.55, 0.45)
        ranked = _rank_evidence([weak, strong])
        assert [c.name for c in ranked] == ["zzz_strong", "aaa_weak"]

    def test_empty_is_empty(self) -> None:
        assert _rank_evidence([]) == ()


# ── Priors override loader ─────────────────────────────────────────────


class TestLoadPriorsOverride:
    def test_missing_file_is_empty(self, tmp_path) -> None:
        assert load_priors_override(tmp_path / "absent.yaml") == {}

    def test_priors_mapping_with_invalid_values_filtered(self, tmp_path) -> None:
        # 1.5 (above) and -0.5 (below) both fall outside the open (0, 1)
        # interval: -0.5 also kills a lower-bound constant mutation
        # (``0.0 < fv`` -> ``-1.0 < fv``) that the above-only case misses.
        f = tmp_path / "p.yaml"
        f.write_text(
            "priors:\n  m365_tenant: 0.5\n  too_high: 1.5\n  too_low: -0.5\n  not_a_number: x\n",
            encoding="utf-8",
        )
        assert load_priors_override(f) == {"m365_tenant": 0.5}

    def test_top_level_mapping_form(self, tmp_path) -> None:
        f = tmp_path / "p.yaml"
        f.write_text("aws_hosting: 0.25\n", encoding="utf-8")
        assert load_priors_override(f) == {"aws_hosting": 0.25}

    def test_non_mapping_yaml_is_empty(self, tmp_path) -> None:
        f = tmp_path / "p.yaml"
        f.write_text("- 1\n- 2\n", encoding="utf-8")
        assert load_priors_override(f) == {}

    def test_malformed_yaml_is_empty(self, tmp_path) -> None:
        f = tmp_path / "p.yaml"
        f.write_text("{unclosed", encoding="utf-8")
        assert load_priors_override(f) == {}


# ── Network lookup ─────────────────────────────────────────────────────


class TestNetworkGet:
    def test_get_known_node(self) -> None:
        net = load_network()
        assert net.get("m365_tenant").name == "m365_tenant"

    def test_get_unknown_node_raises(self) -> None:
        net = load_network()
        with pytest.raises(KeyError):
            net.get("no_such_node")


# ── n_eff arithmetic, pinned exactly ───────────────────────────────────


class TestNEffExactValues:
    # n_eff is an exposed NodePosterior field, so the arithmetic
    # (_MIN_N_EFF + count * _EVIDENCE_N_EFF_CONTRIB - conflicts *
    # _CONFLICT_N_EFF_PENALTY, floored at _MIN_N_EFF) can be pinned to
    # exact values. The values depend on the shipped network's bindings;
    # a deliberate network change that moves them shows up here next to
    # the drift-gate baseline it also has to update.

    def test_one_role_binding(self) -> None:
        net = load_network()
        result = infer(net, [], ["cdn_cname_observed"], priors_override={})
        post = {p.name: p for p in result.posteriors}
        assert post["cdn_fronting"].n_eff == 5.0

    def test_conflict_subtracts_exactly_its_penalty(self) -> None:
        net = load_network()
        result = infer(
            net,
            [],
            ["dmarc_reject", "spf_strict"],
            conflict_field_count=1,
            priors_override={},
        )
        post = {p.name: p for p in result.posteriors}
        # Three applied declarative units plus two firings, less one conflict.
        # the symbolic form moves with a mutation to the constant and so
        # cannot catch it. The constant is cross-checked separately below.
        assert post["email_security_policy_enforcing"].n_eff == 5.5
        assert _CONFLICT_N_EFF_PENALTY == 1.5

    def test_floor_holds_for_evidence_free_node_under_conflict(self) -> None:
        net = load_network()
        result = infer(net, [], [], conflict_field_count=1, priors_override={})
        post = {p.name: p for p in result.posteriors}
        assert post["cdn_fronting"].n_eff == 4.0

    def test_declarative_informative_absences_count(self) -> None:
        # With nothing fired, the declarative policy node still earns
        # n_eff from its informative absences: the absent dmarc_policy
        # group, the absent spf_strict complement, and the weak but non-neutral
        # mta_sts complement. Every absence actually applied by inference is
        # surfaced and counted.
        net = load_network()
        result = infer(net, [], [], priors_override={})
        post = {p.name: p for p in result.posteriors}
        assert post["email_security_policy_enforcing"].n_eff == 7.0

    def test_every_applied_declarative_absence_has_provenance(self) -> None:
        net = load_network()
        post = {p.name: p for p in infer(net, [], [], priors_override={}).posteriors}
        policy = post["email_security_policy_enforcing"]
        absences = {item.unit: item for item in policy.unit_counterfactuals}

        assert policy.absence_informative is True
        assert set(absences) == {"dmarc_policy", "mta_sts_enforce", "spf_strict"}
        assert all(item.observed == "absent" for item in absences.values())
        assert all(item.delta != 0.0 for item in absences.values())

    @pytest.mark.parametrize(("contribution", "expected"), [(3.0, 12.0), (3.4567, 12.46)])
    def test_network_calibration_drives_n_eff_arithmetic(self, contribution: float, expected: float) -> None:
        base = load_network()
        net = BayesianNetwork(
            version=base.version,
            nodes=base.nodes,
            calibration=CalibrationSettings(
                min_n_eff=10.0,
                evidence_n_eff_contrib=contribution,
                conflict_n_eff_penalty=1.0,
            ),
        )
        result = infer(net, [], ["cdn_cname_observed"], conflict_field_count=1, priors_override={})
        post = {p.name: p for p in result.posteriors}
        assert post["cdn_fronting"].n_eff == expected
        assert post["cdn_fronting"].sparse is False

    def test_absence_informative_flag_tracks_declarative_missingness(self) -> None:
        # The exposed ``absence_informative`` field is True for the one
        # declarative node and False for every hideable node. Pinning both
        # sides kills a flip of the ``missingness == "declarative"`` test.
        net = load_network()
        post = {p.name: p for p in infer(net, [], [], priors_override={}).posteriors}
        assert post["email_security_policy_enforcing"].absence_informative is True
        assert post["m365_tenant"].absence_informative is False
        assert post["cdn_fronting"].absence_informative is False


# ── Contract predicates ────────────────────────────────────────────────


class TestContractPredicates:
    # The deal contracts only fire on violation, so on correct code a
    # weakened predicate is invisible to the behavior suites. Pinning
    # the predicates directly keeps the contracts meaning what they say.

    def test_factor_is_probabilities_rejects_out_of_range(self) -> None:
        assignment = frozenset((("n", "present"),))
        assert _factor_is_probabilities({assignment: 0.0})
        assert _factor_is_probabilities({assignment: 0.5})
        assert _factor_is_probabilities({assignment: 1.0})
        assert not _factor_is_probabilities({assignment: -0.5})
        assert not _factor_is_probabilities({assignment: 1.5})

    def test_factor_is_strictly_positive_rejects_zero(self) -> None:
        assignment = frozenset((("n", "present"),))
        assert _factor_is_strictly_positive(None)
        assert _factor_is_strictly_positive({assignment: 1e-9})
        assert not _factor_is_strictly_positive({assignment: 0.0})
        assert not _factor_is_strictly_positive({assignment: -1e-9})

    def test_marginal_in_unit_range(self) -> None:
        assert _marginal_in_unit_range({"present": 0.0, "absent": 1.0})
        assert _marginal_in_unit_range({"present": 0.4, "absent": 0.6})
        assert not _marginal_in_unit_range({"present": -0.1})
        assert not _marginal_in_unit_range({"present": 1.1})

    def test_query_marginal_distinguishes_no_factors_from_zero_mass(self) -> None:
        uniform = {"present": 0.5, "absent": 0.5}
        assert _query_marginal([], "q", []) == uniform

        zero_factor = {
            frozenset((("q", "present"),)): 0.0,
            frozenset((("q", "absent"),)): 0.0,
        }
        with pytest.raises(FloatingPointError, match="invalid normalization mass"):
            _query_marginal([zero_factor], "q", ["q"])

    def test_binding_llr_uses_real_ratio(self) -> None:
        evidence = _ev("ratio", 0.6, 0.4)
        assert math.isclose(_binding_llr(evidence), math.log(1.5), rel_tol=0.0, abs_tol=1e-12)

    def test_interval_is_ordered(self) -> None:
        assert _interval_is_ordered((0.2, 0.8))
        assert not _interval_is_ordered((0.8, 0.2))
        assert not _interval_is_ordered((-0.1, 0.5))
        assert not _interval_is_ordered((0.5, 1.1))


class TestCollectionMaskingContracts:
    @staticmethod
    def _network() -> BayesianNetwork:
        declarative = _Node(
            name="declarative",
            description="Public declaration",
            parents=(),
            prior=0.5,
            cpt={},
            evidence=(_ev("decl-unit", 0.8, 0.2, kind="signal"),),
            missingness="declarative",
            group_absence=(),
        )
        hideable = _Node(
            name="hideable",
            description="Potentially hidden observation",
            parents=(),
            prior=0.5,
            cpt={},
            evidence=(_ev("hide-unit", 0.8, 0.2, kind="signal"),),
            missingness="hideable",
            group_absence=(),
        )
        return BayesianNetwork(version=1, nodes=(declarative, hideable))

    def test_whole_dns_masks_only_declarative_units_from_supplied_network(self) -> None:
        network = self._network()
        masked = collection_masked_units(("dns",), network)
        assert "decl-unit" in masked
        assert "hide-unit" not in masked
        assert collection_masked_units((), network) == frozenset()

    def test_adapter_distinguishes_unobserved_from_informative_absence(self) -> None:
        network = BayesianNetwork(version=1, nodes=(self._network().get("declarative"),))

        absent = infer_from_tenant_info(SimpleNamespace(), network=network, priors_override={}).posteriors[0]
        unobserved = infer_from_tenant_info(
            SimpleNamespace(degraded_sources=("dns",)),
            network=network,
            priors_override={},
        ).posteriors[0]
        doubly_masked = infer_from_tenant_info(
            SimpleNamespace(degraded_sources=("dns",)),
            network=network,
            priors_override={},
            masked_units=("decl-unit",),
        ).posteriors[0]

        assert absent.posterior == 0.2
        assert absent.absence_informative is True
        assert len(absent.unit_counterfactuals) == 1
        assert unobserved.posterior == 0.5
        assert unobserved.absence_informative is False
        assert unobserved.unit_counterfactuals == ()
        assert doubly_masked == unobserved


# ── Output rounding granularity ────────────────────────────────────────


class TestOutputRounding:
    # ``infer`` rounds each exposed numeric field to a fixed number of
    # decimals (4 for posteriors / intervals / entropy, 2 for n_eff). The
    # aggregate test below pins the contract; the per-field exact anchors
    # that follow pin one node's emitted values to hand-recorded literals.
    # Pinning a literal kills the rounding mutants in both directions per
    # field: a 3-decimal emission and a 5-decimal emission both diverge
    # from the recorded 4-decimal value. The aggregate any()/all() form
    # alone cannot catch a single field rounding coarser, because the other
    # fields keep the any() satisfied. The literals depend on the shipped
    # network's bindings; a deliberate network change that moves them shows
    # up here next to the drift-gate baseline it also has to update.

    def test_posteriors_and_intervals_round_to_four_decimals(self) -> None:
        # Every exposed value must already be at 4-decimal granularity (a
        # 5-decimal emission fails the equality), and at least one must
        # carry a nonzero fourth decimal (a 3-decimal emission fails the
        # any()). The per-field anchors below close the single-field gap.
        net = load_network()
        result = infer(
            net,
            [],
            ["m365_tenant_observed", "okta_idp_observed", "dmarc_reject", "spf_strict"],
            priors_override={},
        )
        values = [v for p in result.posteriors for v in (p.posterior, p.interval_low, p.interval_high)]
        assert all(v == round(v, 4) for v in values)
        assert any(round(v, 3) != v for v in values)

    def test_posterior_interval_and_entropy_fields_pinned(self) -> None:
        net = load_network()
        post = {p.name: p for p in infer(net, _RICH_SLUGS, _RICH_SIGNALS, priors_override={}).posteriors}
        m365 = post["m365_tenant"]
        # posterior raw 0.97655696..., interval_low raw 0.88983...: the
        # 4-decimal literal differs from both its 3- and 5-decimal forms.
        assert m365.posterior == 0.9766
        assert m365.interval_low == 0.8898
        # entropy_reduction_nats raw 0.49971224...: a per-node entropy field.
        assert m365.entropy_reduction_nats == 0.4997
        # interval_high is clamped to 1.0 on m365; take an interior node whose
        # exact Beta upper bound stays inside the unit range.
        assert post["google_workspace_tenant"].interval_high == 0.5715

    def test_total_entropy_reduction_rounds_to_four_decimals(self) -> None:
        # The InferenceResult-level total. raw 0.99850...: a 3-decimal
        # emission (0.999) fails the literal, pinning round(_, 4).
        net = load_network()
        result = infer(net, [], ["m365_tenant_observed", "dmarc_reject"], priors_override={})
        assert result.entropy_reduction == 0.9985


class TestUnitCounterfactuals:
    # The exact leave-one-unit-out counterfactual surface (v2.2). Each
    # UnitCounterfactual carries ``posterior_without`` and ``delta =
    # posterior - posterior_without``, both rounded to 4 decimals, and the
    # list is sorted by descending absolute delta (ties by unit name).
    # These fields are exercised only here, so without exact pins the
    # rounding, the delta subtraction, and the sort-key sign all survive
    # mutation. Literals depend on the shipped network (see TestOutputRounding).

    def test_posterior_without_and_delta_pinned(self) -> None:
        net = load_network()
        post = {p.name: p for p in infer(net, _RICH_SLUGS, _RICH_SIGNALS, priors_override={}).posteriors}
        cfs = {c.unit: c for c in post["m365_tenant"].unit_counterfactuals}
        cf = cfs["m365_tenant_observed"]
        # posterior_without raw 0.56812246..., delta raw 0.40843449...: the
        # 4-decimal literals differ from their 3- and 5-decimal forms, and
        # the delta literal also dies under any non-subtraction operator
        # (present + / * / // / % / ** absent diverge by orders of magnitude).
        assert cf.posterior_without == 0.5681
        assert cf.delta == 0.4084

    def test_counterfactuals_sorted_by_descending_absolute_delta(self) -> None:
        # The policy node fires two units with unequal influence. The
        # stronger (dmarc_policy, delta 0.2334) must precede the weaker
        # (spf_strict, delta 0.0132), followed by the applied weak MTA-STS
        # absence (delta -0.0007). An ascending or unsigned sort key flips the
        # order.
        net = load_network()
        post = {p.name: p for p in infer(net, _RICH_SLUGS, _RICH_SIGNALS, priors_override={}).posteriors}
        order = [c.unit for c in post["email_security_policy_enforcing"].unit_counterfactuals]
        assert order == ["dmarc_policy", "spf_strict", "mta_sts_enforce"]


class TestCalibrationLoaderValidation:
    """The calibration block is user-editable, so its parser must reject
    malformed inputs instead of silently coercing them."""

    def test_bool_calibration_value_is_rejected(self) -> None:
        # bool is an int subclass, so ``calibration: {min_n_eff: true}`` would
        # otherwise be read as 1.0. It must raise instead of corrupting the
        # interval math.
        from recon_tool.bayesian_loader import _parse_calibration

        with pytest.raises(ValueError, match="min_n_eff"):
            _parse_calibration({"min_n_eff": True})


# ── TenantInfo adapters ────────────────────────────────────────────────


class TestSignalsFromTenantInfo:
    def test_field_derived_signals(self) -> None:
        info = SimpleNamespace(
            auth_type="Federated",
            dmarc_policy="reject",
            mta_sts_mode="enforce",
            services=(SVC_SPF_STRICT,),
            evidence=(
                SimpleNamespace(source_type="DKIM", raw_value="v=DKIM1", slug="dkim"),
                SimpleNamespace(source_type="SPF", raw_value="v=spf1 -all", slug="spf-strict"),
            ),
        )
        assert signals_from_tenant_info(info) == {
            "m365_tenant_observed",
            "federated_sso_hub",
            "dmarc_reject",
            "mta_sts_enforce",
            "dkim_present",
            "spf_strict",
        }

    def test_quarantine_and_google_federation(self) -> None:
        info = SimpleNamespace(google_auth_type="Federated", dmarc_policy="quarantine")
        assert signals_from_tenant_info(info) == {
            "google_workspace_tenant_observed",
            "federated_sso_hub",
            "dmarc_quarantine",
        }

    def test_dmarc_reject_full_pct_enforces(self) -> None:
        assert "dmarc_reject" in signals_from_tenant_info(SimpleNamespace(dmarc_policy="reject", dmarc_pct=100))
        # pct absent means full coverage (RFC 9989 records carry no pct tag).
        assert "dmarc_reject" in signals_from_tenant_info(SimpleNamespace(dmarc_policy="reject"))

    def test_dmarc_reject_zero_pct_is_monitoring_only(self) -> None:
        # p=reject; pct=0 applies the policy to 0% of mail: monitoring, not
        # enforcement, so neither enforcement signal fires.
        sigs = signals_from_tenant_info(SimpleNamespace(dmarc_policy="reject", dmarc_pct=0))
        assert "dmarc_reject" not in sigs
        assert "dmarc_quarantine" not in sigs

    def test_dmarc_partial_pct_steps_down_one_level(self) -> None:
        # p=reject at partial coverage steps down to quarantine-level; a
        # quarantine at partial coverage steps down to none (no signal).
        reject_partial = signals_from_tenant_info(SimpleNamespace(dmarc_policy="reject", dmarc_pct=50))
        assert "dmarc_reject" not in reject_partial
        assert "dmarc_quarantine" in reject_partial
        quarantine_partial = signals_from_tenant_info(SimpleNamespace(dmarc_policy="quarantine", dmarc_pct=50))
        assert "dmarc_quarantine" not in quarantine_partial
        assert "dmarc_reject" not in quarantine_partial

    def test_dmarc_testing_mode_steps_down_one_level(self) -> None:
        reject_testing = signals_from_tenant_info(SimpleNamespace(dmarc_policy="reject", dmarc_testing=True))
        assert "dmarc_reject" not in reject_testing
        assert "dmarc_quarantine" in reject_testing
        quarantine_testing = signals_from_tenant_info(SimpleNamespace(dmarc_policy="quarantine", dmarc_testing=True))
        assert "dmarc_quarantine" not in quarantine_testing
        assert "dmarc_reject" not in quarantine_testing

    @pytest.mark.parametrize(
        ("info", "expected"),
        [
            (SimpleNamespace(dmarc_policy="reject", dmarc_pct=50, dmarc_testing=True), set()),
            (SimpleNamespace(dmarc_policy="reject", dmarc_pct=100, dmarc_testing=True), {"dmarc_quarantine"}),
            (SimpleNamespace(dmarc_policy="quarantine", dmarc_pct=50, dmarc_testing=True), set()),
        ],
    )
    def test_dmarc_pct_and_testing_compose(self, info: SimpleNamespace, expected: set[str]) -> None:
        assert signals_from_tenant_info(info) == expected

    def test_spf_strict_requires_typed_spf_evidence(self) -> None:
        # Extensible service names cannot satisfy a policy node. The typed SPF
        # record and parser-owned slug are the claim boundary.
        assert signals_from_tenant_info(SimpleNamespace(services=("SPF: softfail (~all)",))) == set()
        assert signals_from_tenant_info(SimpleNamespace(services=(SVC_SPF_STRICT,))) == set()
        assert signals_from_tenant_info(
            SimpleNamespace(
                services=(SVC_SPF_STRICT,),
                evidence=(SimpleNamespace(source_type="SPF", slug="spf-strict"),),
            )
        ) == {"spf_strict"}

    def test_empty_info_yields_nothing(self) -> None:
        assert signals_from_tenant_info(SimpleNamespace()) == set()


class TestConflictProvenance:
    def test_no_conflicts(self) -> None:
        assert _conflict_provenance(SimpleNamespace()) == ()
        assert _conflict_provenance(SimpleNamespace(merge_conflicts=None)) == ()

    def test_dedupes_sources_and_carries_penalty(self) -> None:
        conflicts = SimpleNamespace(
            display_name=(),
            auth_type=(
                SimpleNamespace(source="dns"),
                SimpleNamespace(source="oidc"),
                SimpleNamespace(source="dns"),
            ),
            region=(),
            tenant_id=(),
            dmarc_policy=(),
            google_auth_type=(),
        )
        out = _conflict_provenance(SimpleNamespace(merge_conflicts=conflicts))
        assert len(out) == 1
        assert out[0].field == "auth_type"
        assert out[0].sources == ("dns", "oidc")
        assert out[0].magnitude == _CONFLICT_N_EFF_PENALTY


class TestInferFromTenantInfo:
    def test_slug_observation_survives_adapter_extraction(self) -> None:
        node = _Node(
            name="slug_node",
            description="Slug-backed claim",
            parents=(),
            prior=0.5,
            cpt={},
            evidence=(_ev("probe", 0.8, 0.2),),
            missingness="hideable",
            group_absence=(),
        )
        network = BayesianNetwork(version=1, nodes=(node,))

        posterior = infer_from_tenant_info(
            SimpleNamespace(slugs=("probe",)),
            network=network,
            priors_override={},
        ).posteriors[0]

        assert posterior.posterior == 0.8
        assert posterior.evidence_used == ("slug:probe",)
        assert posterior.unit_counterfactuals[0].posterior_without == 0.5

    def test_role_observation_raises_posterior_and_counts_conflicts(self) -> None:
        net = load_network()
        empty = infer_from_tenant_info(SimpleNamespace(), network=net, priors_override={})
        base = {p.name: p for p in empty.posteriors}
        info = SimpleNamespace(auth_type="Managed")
        result = infer_from_tenant_info(info, network=net, priors_override={})
        post = {p.name: p for p in result.posteriors}
        assert post["m365_tenant"].posterior > base["m365_tenant"].posterior
        assert result.conflict_count == 0

        conflicted = SimpleNamespace(
            auth_type="Managed",
            merge_conflicts=SimpleNamespace(
                display_name=(),
                auth_type=(SimpleNamespace(source="dns"), SimpleNamespace(source="oidc")),
                region=(),
                tenant_id=(),
                dmarc_policy=(),
                google_auth_type=(),
            ),
        )
        result2 = infer_from_tenant_info(conflicted, network=net, priors_override={})
        assert result2.conflict_count == 1
        post2 = {p.name: p for p in result2.posteriors}
        # The conflict lowers n_eff, so the band widens relative to
        # the unconflicted run of the same evidence.
        width = post["m365_tenant"].interval_high - post["m365_tenant"].interval_low
        width2 = post2["m365_tenant"].interval_high - post2["m365_tenant"].interval_low
        assert width2 > width

    def test_conflict_provenance_uses_network_calibration(self) -> None:
        base = load_network()
        net = BayesianNetwork(
            version=base.version,
            nodes=base.nodes,
            calibration=CalibrationSettings(conflict_n_eff_penalty=2.0),
        )
        conflicted = SimpleNamespace(
            auth_type="Managed",
            merge_conflicts=SimpleNamespace(
                display_name=(),
                auth_type=(SimpleNamespace(source="dns"), SimpleNamespace(source="oidc")),
                region=(),
                tenant_id=(),
                dmarc_policy=(),
                google_auth_type=(),
            ),
        )
        result = infer_from_tenant_info(conflicted, network=net, priors_override={})
        post = {p.name: p for p in result.posteriors}
        assert post["m365_tenant"].conflict_provenance[0].magnitude == 2.0
