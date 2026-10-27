"""Synthetic outcome-observation contract tests."""

from devrar.epeisodia import axiologise_epeisodia


def test_asxeto_citation_den_apodeiknyei_uncited_outcome() -> None:
    """Μετρητές άλλων events δεν δίνουν status στο άσχετο cited output."""
    apotelesma = axiologise_epeisodia(
        {
            "metrika_ergasias": {
                "epeisodia": [
                    {
                        "tests_passed": 100,
                        "tests_failed": 10,
                        "exit_success": 5,
                        "exit_failure": 2,
                        "tekmiria": [
                            {
                                "eidos": "tool_result",
                                "apospasma": "directory listing",
                            }
                        ],
                    }
                ]
            }
        }
    )
    assert apotelesma["epeisodia_ergasias"]["paratiriseis"][0]["katastasi"] == "unknown"


def test_native_command_outcomes_menoun_xoristo_channel() -> None:
    """Η native έξοδος δεν προστίθεται στους global counters ή στα global episodes."""
    native = {"metrika_ergasias": {"epeisodia": [{
        "id": "W0001", "pigi": "Codex native command events", "synedria": "s1",
        "exit_success": 1, "tekmiria": [{
            "eidos": "tool_result", "rolos": "tool", "kodikos_exodou": 0,
            "apospasma": "Synthetic output", "locator": "native-command-a",
        }],
    }]}}
    dedomena = {"codex_native": native, "metrika_ergasias": {"epeisodia": []}}
    apotelesma = axiologise_epeisodia(dedomena)
    assert apotelesma["epeisodia_ergasias"]["paratiriseis"] == []
    paratiriseis = apotelesma["codex_native"]["epeisodia_ergasias"]["paratiriseis"]
    assert paratiriseis[0]["katastasi"] == "observed_success"
    assert "epeisodia_ergasias" not in native


def test_axiologise_epeisodia_syndeei_paratirisi_me_tool_result() -> None:
    """Ελέγχει παρατήρηση επιτυχίας με ακριβές tool-result citation."""
    dedomena: dict[str, object] = {
        "metrika_ergasias": {
            "epeisodia": [
                {
                    "id": "episode-1",
                    "pigi": "Synthetic CLI",
                    "synedria": "session-a",
                    "prompts": 2,
                    "tool_calls": 1,
                    "tool_results": 1,
                    "tests_passed": 2,
                    "tests_failed": 0,
                    "tests_skipped": 0,
                    "exit_success": 1,
                    "exit_failure": 0,
                    "tekmiria_included": 1,
                    "tekmiria_eligible": 2,
                    "tekmiria_truncated": True,
                    "tekmiria": [
                        {
                            "id": "result-1",
                            "pigi": "Synthetic CLI",
                            "synedria": "session-a",
                            "rolos": "tool",
                            "eidos": "tool_result",
                            "locator": "synthetic.jsonl:9",
                            "keimeno": "=== 2 passed in 0.1s ===",
                        }
                    ],
                }
            ]
        }
    }

    apotelesma = axiologise_epeisodia(dedomena)

    paratirisi = apotelesma["epeisodia_ergasias"]["paratiriseis"][0]
    assert paratirisi["katastasi"] == "observed_success"
    assert paratirisi["kalypsi_tekmirion"] == {
        "included": 1,
        "eligible": 2,
        "truncated": True,
    }
    assert paratirisi["tekmiria"][0] == {
        "id": "result-1",
        "pigi": "Synthetic CLI",
        "synedria": "session-a",
        "locator": "synthetic.jsonl:9",
        "apospasma": "=== 2 passed in 0.1s ===",
    }
    assert apotelesma["metrika_ergasias"] == dedomena["metrika_ergasias"]


def test_axiologise_epeisodia_unknown_and_mixed_evidence_stay_bounded() -> None:
    """Ελέγχει άγνωστα outcomes και ότι prompt claims δεν γίνονται evidence."""
    dedomena: dict[str, object] = {
        "metrika_ergasias": {
            "epeisodia": [
                {
                    "id": "episode-unknown",
                    "pigi": "Synthetic",
                    "synedria": "s-unknown",
                    "prompts": 1,
                    "tool_calls": 0,
                    "tool_results": 0,
                    "tests_passed": None,
                    "tests_failed": None,
                    "tests_skipped": None,
                    "exit_success": 0,
                    "exit_failure": 0,
                    "tekmiria": [
                        {
                            "id": "assistant-1",
                            "rolos": "assistant",
                            "eidos": "response",
                            "locator": "line:1",
                            "keimeno": "All tests passed",
                        }
                    ],
                },
                {
                    "id": "episode-mixed",
                    "pigi": "Synthetic",
                    "synedria": "s-mixed",
                    "prompts": 1,
                    "tool_calls": 2,
                    "tool_results": 2,
                    "tests_passed": 1,
                    "tests_failed": 1,
                    "tests_skipped": 0,
                    "exit_success": 1,
                    "exit_failure": 1,
                    "tekmiria": [
                        {
                            "id": "fail-1",
                            "rolos": "tool",
                            "eidos": "tool_result",
                            "locator": "line:8",
                            "keimeno": "=== 1 failed in 0.1s ===",
                        },
                        {
                            "id": "success-1",
                            "rolos": "tool",
                            "eidos": "tool_result",
                            "locator": "line:9",
                            "keimeno": "=== 1 passed in 0.1s ===",
                        },
                    ],
                },
            ]
        }
    }

    apotelesma = axiologise_epeisodia(dedomena)

    paratiriseis = apotelesma["epeisodia_ergasias"]["paratiriseis"]
    assert [eggrafi["katastasi"] for eggrafi in paratiriseis] == [
        "unknown",
        "mixed",
    ]
    assert paratiriseis[0]["tekmiria"] == []
    assert len(apotelesma["epeisodia_ergasias"]["proteraiotites"]) <= 3


def test_axiologise_epeisodia_propagates_episode_truncation() -> None:
    """Ελέγχει ότι cap metadata του metrics reader δεν χάνεται."""
    dedomena: dict[str, object] = {
        "metrika_ergasias": {
            "episodes_included": 1,
            "episodes_eligible": 4,
            "episodes_truncated": True,
            "epeisodia": [],
        }
    }

    apotelesma = axiologise_epeisodia(dedomena)

    assert apotelesma["epeisodia_ergasias"]["katastasi"] == "partial"
    assert apotelesma["epeisodia_ergasias"]["kalypsi"] == {
        "diathesima": 4,
        "analysimena": 1,
        "perikopi": True,
    }


def test_axiologise_epeisodia_metadata_without_citation_remains_unknown() -> None:
    """Ελέγχει ότι counters και truncated citations δεν τεκμηριώνουν outcome."""
    dedomena: dict[str, object] = {
        "metrika_ergasias": {
            "epeisodia": [
                {
                    "id": "episode-no-citation",
                    "pigi": "Synthetic",
                    "synedria": "s-no-citation",
                    "tests_passed": 3,
                    "tests_failed": 0,
                    "tests_skipped": 0,
                    "exit_success": 0,
                    "exit_failure": 0,
                    "tekmiria": [],
                    "tekmiria_included": 0,
                    "tekmiria_eligible": 1,
                    "tekmiria_truncated": True,
                }
            ]
        }
    }

    apotelesma = axiologise_epeisodia(dedomena)

    paratirisi = apotelesma["epeisodia_ergasias"]["paratiriseis"][0]
    assert paratirisi["katastasi"] == "unknown"
    assert paratirisi["metrisi"]["tests_passed"] == 3
    assert paratirisi["periorismoi"] == [
        "Evidence citations are truncated; aggregate counters alone "
        "do not verify an outcome."
    ]


def test_axiologise_epeisodia_failure_and_exit_code_are_cited() -> None:
    """Ελέγχει failure evidence και locator exit-code citation."""
    dedomena: dict[str, object] = {
        "metrika_ergasias": {
            "epeisodia": [
                {
                    "pigi": "Synthetic",
                    "synedria": "s-failure",
                    "tests_passed": None,
                    "tests_failed": 1,
                    "tests_skipped": None,
                    "exit_success": 0,
                    "exit_failure": 1,
                    "tekmiria": [
                        {
                            "id": "exit-fail",
                            "pigi": "Synthetic",
                            "synedria": "s-failure",
                            "locator": "synthetic.jsonl:20",
                            "eidos": "tool_result",
                            "kodikos_exodou": 1,
                            "keimeno": "exit 1",
                        }
                    ],
                }
            ]
        }
    }

    apotelesma = axiologise_epeisodia(dedomena)

    paratirisi = apotelesma["epeisodia_ergasias"]["paratiriseis"][0]
    assert paratirisi["katastasi"] == "observed_failure"
    assert paratirisi["id"] == "episode-1"
    assert paratirisi["dynata_simeia"] == []
    assert paratirisi["tekmiria"][0]["kodikos_exodou"] == "1"


def test_axiologise_epeisodia_exit_code_only_derives_outcome() -> None:
    """Ελέγχει exit evidence ως outcome όταν δεν υπάρχει test summary."""
    dedomena: dict[str, object] = {
        "metrika_ergasias": {
            "epeisodia": [
                {
                    "id": "episode-exit",
                    "pigi": "Synthetic",
                    "synedria": "s-exit",
                    "tests_passed": None,
                    "tests_failed": None,
                    "tests_skipped": None,
                    "exit_success": 0,
                    "exit_failure": 0,
                    "tekmiria": [
                        {
                            "id": "exit-0",
                            "pigi": "Synthetic",
                            "synedria": "s-exit",
                            "locator": "synthetic.jsonl:2",
                            "eidos": "tool_result",
                            "kodikos_exodou": 0,
                            "apospasma": "command completed",
                        }
                    ],
                }
            ]
        }
    }

    apotelesma = axiologise_epeisodia(dedomena)

    paratirisi = apotelesma["epeisodia_ergasias"]["paratiriseis"][0]
    assert paratirisi["katastasi"] == "observed_success"
    assert paratirisi["tekmiria"][0]["apospasma"] == "command completed"


def test_axiologise_epeisodia_tool_result_without_outcome_stays_unknown() -> None:
    """Ελέγχει tool result χωρίς status/counts ως unknown και όχι success."""
    apotelesma = axiologise_epeisodia(
        {
            "metrika_ergasias": {
                "epeisodia": [
                    {
                        "id": "episode-output-only",
                        "pigi": "Synthetic",
                        "synedria": "s-output-only",
                        "tests_passed": None,
                        "tests_failed": None,
                        "tests_skipped": None,
                        "exit_success": 0,
                        "exit_failure": 0,
                        "tekmiria": [
                            {
                                "id": "output-only",
                                "pigi": "Synthetic",
                                "synedria": "s-output-only",
                                "locator": "synthetic.jsonl:4",
                                "eidos": "tool_result",
                                "apospasma": "completed",
                            }
                        ],
                    }
                ]
            }
        }
    )

    paratirisi = apotelesma["epeisodia_ergasias"]["paratiriseis"][0]

    assert paratirisi["katastasi"] == "unknown"
    assert paratirisi["vevaiotita"] == "low"


def test_axiologise_epeisodia_filters_malformed_episode_container() -> None:
    """Ελέγχει malformed container ως unknown χωρίς crashes ή counts inventing."""
    apotelesma = axiologise_epeisodia({"metrika_ergasias": {"epeisodia": "not-a-list"}})

    assert apotelesma["epeisodia_ergasias"]["katastasi"] == "unknown"
    assert apotelesma["epeisodia_ergasias"]["paratiriseis"] == []


def test_axiologise_epeisodia_caps_episodes_without_score_gate() -> None:
    """Ελέγχει bounded output και uncalibrated score gate for large input."""
    episodes = [
        {
            "id": f"episode-{index}",
            "pigi": "Synthetic",
            "synedria": f"s-{index}",
            "tests_passed": None,
            "tests_failed": None,
            "tests_skipped": None,
            "exit_success": 0,
            "exit_failure": 0,
            "tekmiria": [],
        }
        for index in range(101)
    ]

    apotelesma = axiologise_epeisodia({"metrika_ergasias": {"epeisodia": episodes}})

    report = apotelesma["epeisodia_ergasias"]
    assert len(report["paratiriseis"]) == 100
    assert report["kalypsi"]["perikopi"] is True
    assert report["vathmologisi_energi"] is False
