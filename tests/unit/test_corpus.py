"""Invariants for the generated synthetic corpus.

These tests only cover corpus generation. Ingestion, retrieval and the rest of
the platform are out of scope here.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "corpus"
TENANTS = ["tenant-alpha", "tenant-beta"]
REQUIRED_KEYS = [
    "tenant",
    "tenant_name",
    "doc_id",
    "source_id",
    "title",
    "equipment",
    "document_type",
    "revision",
    "effective_date",
    "status",
]


def read_manifest() -> dict:
    return json.loads((CORPUS / "manifest.json").read_text(encoding="utf-8"))


def flatten(text: str) -> str:
    """Collapse line wrapping so assertions are not defeated by the layout."""
    return re.sub(r"\s+", " ", text)


def front_matter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "---"
    values = {}
    for line in lines[1:]:
        if line == "---":
            break
        key, _, value = line.partition(":")
        values[key.strip()] = value.strip().strip('"')
    return values


def documents_of(tenant: str) -> list[Path]:
    return sorted((CORPUS / tenant).glob("*.md"))


def test_corpus_is_regenerated_from_the_generator():
    result = subprocess.run(
        [sys.executable, "scripts/generate_corpus.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_corpus_has_exactly_two_tenants_with_at_least_thirty_documents():
    manifest = read_manifest()
    assert [entry["tenant"] for entry in manifest["tenants"]] == TENANTS
    assert manifest["document_count"] >= 30

    counts = {tenant: len(documents_of(tenant)) for tenant in TENANTS}
    assert all(count >= 15 for count in counts.values()), counts
    assert max(counts.values()) - min(counts.values()) <= 1, counts


def test_every_document_declares_its_metadata():
    manifest = read_manifest()
    seen = set()
    for entry in manifest["documents"]:
        path = CORPUS / entry["path"]
        values = front_matter(path)
        for key in REQUIRED_KEYS:
            assert values.get(key), f"{entry['path']} is missing {key}"
        assert values["tenant"] == entry["tenant"]
        assert values["doc_id"] not in seen
        seen.add(values["doc_id"])
        assert len(values["equipment"]) >= 4
        assert path.read_text(encoding="utf-8").count("\n## ") >= 5


def test_revisions_are_paired_and_differ_in_content():
    manifest = read_manifest()
    revisions = [entry for entry in manifest["documents"] if entry["revision"].startswith("Rev ")]
    pairs = {}
    for entry in revisions:
        stem = re.sub(r"-[AB]$", "", entry["doc_id"])
        pairs.setdefault(stem, []).append(entry)

    paired = {stem: group for stem, group in pairs.items() if len(group) == 2}
    assert len(paired) >= 3, sorted(pairs)

    for stem, group in paired.items():
        first, second = sorted(group, key=lambda entry: entry["revision"])
        assert first["revision"] == "Rev A"
        assert second["revision"] == "Rev B"
        assert first["status"] == "superseded"
        assert second["status"] == "current"
        assert second["supersedes"] == first["doc_id"]
        assert first["effective_date"] < second["effective_date"]
        assert first["sha256"] != second["sha256"], stem


def test_conflicting_revisions_carry_different_values():
    manual_a = (CORPUS / "tenant-alpha" / "hydraulic-press-manual-rev-a.md").read_text(encoding="utf-8")
    manual_b = (CORPUS / "tenant-alpha" / "hydraulic-press-manual-rev-b.md").read_text(encoding="utf-8")
    assert "240 bar" in manual_a and "210 bar" in manual_b
    assert "500 running hours" in manual_a and "300 running hours" in manual_b

    beta_a = (CORPUS / "tenant-beta" / "hydraulic-press-manual-rev-a.md").read_text(encoding="utf-8")
    beta_b = (CORPUS / "tenant-beta" / "hydraulic-press-manual-rev-b.md").read_text(encoding="utf-8")
    assert "2000 psi" in beta_a and "1750 psi" in beta_b


def test_corpus_contains_the_intended_difficult_cases():
    corpus_text = "\n".join(
        path.read_text(encoding="utf-8")
        for tenant in TENANTS
        for path in documents_of(tenant)
    )
    assert "insufficient information" in corpus_text, "missing-information cases"
    assert "Attempt start" in corpus_text, "zero-energy verification"
    assert "zero-energy verification tag" in corpus_text, "safety prerequisites"
    assert "Documentation gaps" in corpus_text, "declared documentation gaps"
    assert "HP-200B" in corpus_text and "HP-210" in corpus_text, "similar equipment names"
    assert "five or more possible causes" in corpus_text, "ambiguous symptoms"
    assert "Escalate" in corpus_text, "escalation conditions"


def test_tenant_specific_values_do_not_overlap():
    alpha = (CORPUS / "tenant-alpha" / "hydraulic-press-manual-rev-b.md").read_text(encoding="utf-8")
    beta = (CORPUS / "tenant-beta" / "hydraulic-press-manual-rev-b.md").read_text(encoding="utf-8")
    assert "210 bar" in alpha and "210 bar" not in beta
    assert "1750 psi" in beta and "1750 psi" not in alpha

    alpha_chiller = (CORPUS / "tenant-alpha" / "chiller-alarm-troubleshooting-guide.md").read_text(
        encoding="utf-8"
    )
    beta_chiller = (CORPUS / "tenant-beta" / "chiller-alarm-troubleshooting.md").read_text(encoding="utf-8")
    assert "A01" in alpha_chiller and "A01" not in beta_chiller
    assert "F-13" in beta_chiller and "F-13" not in alpha_chiller


def test_pdf_format_samples_are_committed_and_match_their_markdown_source():
    manifest = read_manifest()
    samples = manifest["format_samples"]
    assert 2 <= len(samples) <= 10, len(samples)

    by_doc_id = {entry["doc_id"]: entry for entry in manifest["documents"]}
    tenants = set()
    document_types = set()

    for sample in samples:
        assert sample["document_format"] == "pdf"
        source = CORPUS / sample["source_path"]
        pdf = CORPUS / sample["path"]
        assert source.suffix == ".md" and source.exists(), sample
        assert pdf.suffix == ".pdf" and pdf.exists(), sample
        assert pdf.with_suffix(".md") == source

        data = pdf.read_bytes()
        assert data.startswith(b"%PDF-"), sample["path"]
        assert data.rstrip().endswith(b"%%EOF"), sample["path"]
        assert hashlib.sha256(data).hexdigest() == sample["sha256"], sample["path"]

        entry = by_doc_id[sample["doc_id"]]
        assert entry["path"] == sample["source_path"], sample["path"]
        assert entry["tenant"] == sample["tenant"] == source.parent.name
        tenants.add(sample["tenant"])
        document_types.add(entry["document_type"])

    assert tenants == set(TENANTS), tenants
    assert len(document_types) >= 2, document_types

    committed = {
        path.relative_to(CORPUS).as_posix()
        for tenant in TENANTS
        for path in (CORPUS / tenant).glob("*.pdf")
    }
    assert committed == {sample["path"] for sample in samples}


def test_corpus_contains_no_credentials_or_personal_data():
    forbidden = [
        r"(?i)password\s*[:=]",
        r"(?i)api[_-]?key\s*[:=]",
        r"(?i)secret\s*[:=]",
        r"(?i)bearer\s+[a-z0-9]{10,}",
        r"\b\d{3}-\d{2}-\d{4}\b",
        r"[\w.+-]+@[\w-]+\.[\w.]+",
    ]
    for tenant in TENANTS:
        for path in documents_of(tenant) + [CORPUS / "manifest.json"]:
            text = path.read_text(encoding="utf-8")
            for pattern in forbidden:
                assert not re.search(pattern, text), f"{path} matches {pattern}"


# --- quality review regressions -------------------------------------------------
#
# Each test below locks a defect found in the corpus quality review. They assert
# the corrected content, not the absence of a phrase, so that a future edit which
# reintroduces the contradiction fails loudly.

PRESS_REV_B = CORPUS / "tenant-alpha" / "hydraulic-press-manual-rev-b.md"
PRESS_REV_A = CORPUS / "tenant-alpha" / "hydraulic-press-manual-rev-a.md"


def test_rev_b_tie_rod_interval_does_not_contradict_its_variant_table():
    """Rev B stated 2000 h in one table and 3000 h in another."""
    rev_a = PRESS_REV_A.read_text(encoding="utf-8")
    rev_b = PRESS_REV_B.read_text(encoding="utf-8")

    def summary_interval(text: str) -> int:
        """The HP-200 interval from the one-line technical data entry."""
        match = re.search(
            r"Tie-rod nut torque \| [\d.]+ N\.m, re-torque every (\d+) running hours", text
        )
        assert match, "tie-rod summary line not found"
        return int(match.group(1))

    def variant_intervals(text: str) -> tuple[int, int]:
        """The HP-200 and HP-200B intervals from the variant comparison table."""
        match = re.search(
            r"\| Tie-rod re-torque interval \| (\d+) running hours \| (\d+) running hours \|", text
        )
        assert match, "tie-rod variant row not found"
        return int(match.group(1)), int(match.group(2))

    # The summary line and the variant table must agree inside one revision.
    assert summary_interval(rev_a) == variant_intervals(rev_a)[0]
    assert summary_interval(rev_b) == variant_intervals(rev_b)[0]

    # Rev A is 4000/3000, Rev B is 2000/1500. The stale 3000 h must not survive
    # in Rev B, which is the defect the review found.
    assert variant_intervals(rev_a) == (4000, 3000)
    assert variant_intervals(rev_b) == (2000, 1500)

    # No other tie-rod line in Rev B may reintroduce the Rev A interval.
    for line in rev_b.splitlines():
        if "Tie-rod" in line:
            assert "3000 running hours" not in line, line


def test_safety_valve_acceptance_bands_are_ordered_and_bounded():
    """Both compressors stated 9/10 bar and 135/150 psi as an unordered pair."""
    alpha_pm = flatten(
        (CORPUS / "tenant-alpha" / "air-compressor-preventive-maintenance.md").read_text(
            encoding="utf-8"
        )
    )
    beta_pm = flatten(
        (CORPUS / "tenant-beta" / "air-compressor-preventive-maintenance.md").read_text(
            encoding="utf-8"
        )
    )

    # Each band must name which value is the lower and which the upper bound.
    assert (
        "maximum permissible working pressure of 9.0 bar, which is the lower bound of the band, "
        "and the set pressure of 10.0 bar, which is the upper bound" in alpha_pm
    ), alpha_pm[alpha_pm.index("full lift between") :][:400]

    assert (
        "maximum permissible working pressure of 135 psi, which is the lower bound of the band, "
        "and the set pressure of 150 psi, which is the upper bound" in beta_pm
    ), beta_pm[beta_pm.index("full lift between") :][:400]

    # The set pressure the technician adjusts to is the upper bound in both.
    assert "lifts above the set pressure of 150 psi" in beta_pm
    assert "the receiver is isolated" in beta_pm

    # The two values must never appear in the wrong order.
    assert "10.0 bar, 9.0 bar" not in alpha_pm
    assert "150 psi, 135 psi" not in beta_pm


def test_chiller_rating_condition_and_operating_set_point_are_distinguished():
    """45 degF rating and 46 degF set point read as a contradiction."""
    beta_chiller = flatten(
        (CORPUS / "tenant-beta" / "chiller-alarm-troubleshooting.md").read_text(encoding="utf-8")
    )
    # The table must label the capacity figure as a rating condition.
    assert "Nominal capacity, at rating condition" in beta_chiller
    assert "450 kW cooling at 45 degF leaving water" in beta_chiller
    # The set point must be labelled as the operating value, not the rating.
    assert "supply set point of 46 degF is the operating value" in beta_chiller
    # The document must say which figure answers which kind of question.
    assert (
        "what the machine is capable of must be answered with the 45 degF rating condition"
        in beta_chiller
    )
    assert (
        "what the plant is running to must be answered with the 46 degF operating set point"
        in beta_chiller
    )
    # The technical data table must not relabel the capacity figure as the
    # operating value.
    assert not re.search(r"Nominal capacity, at operating set point", beta_chiller)


def headings_of(text: str) -> set[str]:
    """Heading titles of a document, taken from the unflattened text."""
    return {
        heading.strip().rstrip(".").lower()
        for heading in re.findall(r"^#{1,6}\s+(.+)$", text, re.MULTILINE)
    }


def test_numeric_section_references_resolve_to_a_heading_in_the_same_document():
    """Positional references drifted when sections were inserted or reordered."""
    offenders = []
    for tenant in TENANTS:
        for path in documents_of(tenant):
            text = path.read_text(encoding="utf-8")
            headings = headings_of(text)
            # Scan the flattened text so a reference broken across two lines is found.
            for match in re.finditer(r"\b[Ss]ections?\s+\d+", flatten(text)):
                number = re.search(r"\d+", match.group(0)).group(0)
                if not any(
                    re.match(rf"(?:section\s+)?{number}[\.:]\s*\S", heading)
                    for heading in headings
                ):
                    offenders.append(f"{path.name}: {match.group(0)!r}")
    assert not offenders, offenders


def test_cross_document_references_use_canonical_identifiers():
    """Body prose used AM-/BM- prefixes for documents that exist as ALPHA-/BETA-."""
    wrong_prefix = {
        "AM-DIA-P100-1": "ALPHA-DIA-P100-1",
        "AM-SAF-HP200-LOTO-1": "ALPHA-SAF-HP200-LOTO-1",
        "AM-SAF-OC5T-INS-1": "ALPHA-SAF-OC5T-INS-1",
        "BM-DIA-P100-1": "BETA-DIA-P100-1",
        "BM-SAF-HP200-ECP-1": "BETA-SAF-HP200-ECP-1",
        "BM-SAF-OC5T-INS-1": "BETA-SAF-OC5T-INS-1",
        "BM-TS-HP200-1": "BETA-TS-HP200-1",
    }

    # Assert per document rather than against one concatenated corpus string, so a
    # failure names the file instead of diffing the whole corpus.
    stale_found: list[str] = []
    cited: set[str] = set()
    for tenant in TENANTS:
        for path in documents_of(tenant):
            text = flatten(path.read_text(encoding="utf-8"))
            for stale, correct in wrong_prefix.items():
                if stale in text:
                    stale_found.append(f"{path.name} cites {stale} instead of {correct}")
                if correct in text:
                    cited.add(correct)
    assert not stale_found, stale_found

    # The corrections must actually be present, not merely the old text removed.
    missing = sorted(set(wrong_prefix.values()) - cited)
    assert not missing, f"no longer cited anywhere: {missing}"


def test_referenced_topics_exist_in_the_document_that_cites_them():
    """`under <heading>` pointers must name a heading the citing document has."""
    topic_reference = re.compile(
        r"\b(?:ALPHA|BETA)-[A-Z0-9-]+\b[^.\n]{0,90}?\bunder "
        r"([A-Za-z][A-Za-z0-9 ,\-]{6,70}?)\s*[.;|)\"]"
    )
    checked = 0
    for tenant in TENANTS:
        for path in documents_of(tenant):
            text = path.read_text(encoding="utf-8")
            headings = headings_of(text)
            for match in topic_reference.finditer(text):
                topic = match.group(1).strip().rstrip(".").lower()
                # "serviced under work instruction WI-2204" names a deliberately
                # absent document, not a heading of this corpus.
                if "work instruction" in topic:
                    continue
                assert topic in headings, f"{path.name} points at missing heading {topic!r}"
                checked += 1
    assert checked >= 8, f"only {checked} topic references exercised"


def test_equipment_also_covers_never_claims_coverage_it_denies():
    """Front matter claimed variant coverage that the body declared out of scope."""
    claims = ("none; see section", "see section 10", "see section 7", "see section 8")
    for tenant in TENANTS:
        for path in documents_of(tenant):
            also = front_matter(path).get("equipment_also_covers", "")
            for phrase in claims:
                assert phrase not in also, f"{path.name}: {also!r}"

    # The Beta press troubleshooting guide covers only the straight-side press,
    # so mentioning HP-200S must be an exclusion, never a coverage claim.
    guide = CORPUS / "tenant-beta" / "hydraulic-press-troubleshooting-guide.md"
    guide_covers = front_matter(guide)["equipment_also_covers"]
    assert guide_covers.startswith("none"), guide_covers
    assert "out of scope" in guide_covers, guide_covers
    # The exclusion must be stated in the body, in a scope section rather than
    # buried in an unrelated symptom section.
    guide_text = guide.read_text(encoding="utf-8")
    scope = guide_text.split("## How to use this guide", 1)[1].split("\n## ", 1)[0]
    assert "HP-200S" in scope, scope

    # The Beta press manuals state the HP-200S exclusion in Documentation gaps.
    beta_manual = (CORPUS / "tenant-beta" / "hydraulic-press-manual-rev-b.md").read_text(
        encoding="utf-8"
    )
    gaps = beta_manual.split("## Documentation gaps", 1)[1].split("\n## ", 1)[0]
    assert "WI-2204" in gaps and "HP-200S" in gaps, gaps


def test_absent_document_references_are_listed_in_the_readme():
    """A reader must be able to confirm that a cited document is really absent."""
    readme = (CORPUS / "README.md").read_text(encoding="utf-8")
    manifest = read_manifest()
    canonical = {entry["doc_id"] for entry in manifest["documents"]}

    referenced: set[str] = set()
    for tenant in TENANTS:
        for path in documents_of(tenant):
            text = path.read_text(encoding="utf-8")
            referenced.update(re.findall(r"\b[AB]M-[A-Z]{2,4}-[A-Z0-9]+(?:-[A-Z0-9]+)*\b", text))

    source_register = {token for token in referenced if token not in canonical}
    # Drop part numbers, asset tags and source identifiers, which are not documents.
    source_register = {
        token
        for token in source_register
        if re.match(r"^(?:AM|BM)-(?:MAN|PM|SAF|TS|DIA)-", token)
    }
    assert source_register, "expected register-style document references"

    for token in sorted(source_register):
        assert token in readme, f"{token} is referenced but not listed in corpus/README.md"


def test_hpu_test_six_energization_is_not_contradicted_by_its_own_prerequisites():
    """Test 6 needs an energized motor; the prerequisite list mandates isolation."""
    cases = {
        "tenant-alpha": ("ALPHA-SAF-HP200-LOTO-1", "contamination assessment"),
        "tenant-beta": ("BETA-SAF-HP200-ECP-1", "duplex pump changeover test"),
    }
    for tenant, (energy_control, test_five) in cases.items():
        text = (CORPUS / tenant / "hydraulic-power-unit-diagnostic-procedure.md").read_text(
            encoding="utf-8"
        )
        headings = re.findall(r"^## (.+)$", text, re.MULTILINE)
        assert "Safety prerequisites" in headings
        assert [h for h in headings if re.match(r"Test \d+:", h)] == [
            "Test 1: suction pressure and cavitation check",
            "Test 2: main relief valve lift-off and seating",
            "Test 3: flow measurement",
            "Test 4: pressure decay test",
            f"Test 5: {test_five}",
            "Test 6: motor and drive",
        ]

        prerequisites = flatten(text.split("## Safety prerequisites", 1)[1].split("## Test 1", 1)[0])
        assert "electrical isolation" in prerequisites
        assert f"{energy_control} steps" in prerequisites
        # The exception must be stated where the isolation is mandated.
        assert "Test 6 is an exception to the isolation requirement" in prerequisites
        assert "energization permit" in prerequisites
        assert "no hydraulic work may be in progress" in prerequisites


# --- follow-up review regressions -------------------------------------------------
#
# Each test below locks one of the four issues found after the quality review:
# the corpus page count, the embedded indirect prompt-injection cases, the
# normalised safety prerequisites heading, and pypdf parsing of the committed
# PDF samples.

MINIMUM_PDF_PAGES = 150


def _scripts_on_path() -> None:
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)


def test_corpus_renders_to_at_least_the_required_number_of_pdf_pages():
    """The corpus must render to at least 150 pages, not the original 121.

    Page count is measured with the same exporter that produces the committed
    PDF samples, so the assertion tracks the real artefact rather than a proxy.
    """

    _scripts_on_path()
    from export_corpus_pdf import render as render_pdf
    from generate_corpus import all_documents
    from generate_corpus import render as render_markdown

    total = sum(render_pdf(render_markdown(doc))[1] for doc in all_documents())
    assert total >= MINIMUM_PDF_PAGES, f"corpus renders to only {total} pages"


def test_corpus_embeds_indirect_prompt_injection_cases():
    """At least three documents must carry an untrusted embedded instruction.

    Every case must be labelled as an indirect prompt-injection case so that a
    reader or a retrieval pipeline can tell it apart from approved text.
    """

    marker = "UNTRUSTED EMBEDDED INSTRUCTION"
    label = "indirect prompt-injection case"
    cases = 0
    tenants_seen = set()
    for tenant in TENANTS:
        for path in documents_of(tenant):
            text = path.read_text(encoding="utf-8")
            if marker not in text:
                continue
            assert label in text, f"{path} carries an unlabelled embedded instruction"
            cases += text.count(marker)
            tenants_seen.add(tenant)
    assert cases >= 3, f"only {cases} indirect prompt-injection case(s) found"
    assert tenants_seen == set(TENANTS), tenants_seen


def test_safety_prerequisites_heading_is_stable_and_discoverable():
    """The heading must be exactly `Safety prerequisites`, not a sentence.

    A stable heading is what lets a reader or parser find the prerequisites
    section without guessing at a trailing clause.
    """

    for tenant in TENANTS:
        text = (CORPUS / tenant / "hydraulic-power-unit-diagnostic-procedure.md").read_text(
            encoding="utf-8"
        )
        headings = re.findall(r"^## (.+)$", text, re.MULTILINE)
        assert "Safety prerequisites" in headings, tenant
        unstable = [heading for heading in headings if heading.startswith("Safety prerequisites,")]
        assert not unstable, f"{tenant} has an unstable prerequisites heading: {unstable}"


def test_pdf_format_samples_parse_and_yield_text_with_pypdf():
    """Every committed PDF must be readable and carry extractable text.

    Before the exporter fix all six PDFs reported zero pages to pypdf; this
    test fails if that class of broken PDF returns.
    """

    from pypdf import PdfReader

    manifest = read_manifest()
    samples = manifest["format_samples"]
    assert samples, "no PDF samples registered in the manifest"
    for sample in samples:
        reader = PdfReader(str(CORPUS / sample["path"]))
        assert len(reader.pages) >= 1, sample["path"]
        text = " ".join(
            " ".join((page.extract_text() or "").split()) for page in reader.pages
        )
        assert text, f"{sample['path']} has no extractable text"
        assert sample["title"] in text, f"{sample['path']} does not contain its own title"


def test_appendix_consistency():
    """Verify appendix values match main body values."""
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    corpus = root / "corpus"

    # Alpha air-compressor PM
    alpha_ac = (corpus / "tenant-alpha" / "air-compressor-preventive-maintenance.md").read_text(encoding="utf-8")
    assert "ISO VG 100 synthetic ester, Alpha specification AM-CO-100S" in alpha_ac
    assert "Compressor oil | ISO VG 100 synthetic ester, Alpha specification AM-CO-100S" in alpha_ac
    assert "AM-C46" not in alpha_ac
    assert "Air filter element | pleated, class F7 | 1 | every 4000 running hours" in alpha_ac

    # Beta conveyor/gearmotor
    beta_cv = (corpus / "tenant-beta" / "gearmotor-and-conveyor-maintenance.md").read_text(encoding="utf-8")
    assert "Gearmotor lubricant | 6000 h" in beta_cv
    assert "Belt tracking | Weekly | Belt centred within 0.25 in" in beta_cv


SAFETY_PREREQUISITES_HEADING = "## Safety prerequisites"

# Documents that are dedicated lockout / energy-control procedures rather than
# maintenance or diagnostic procedures. They state their own isolation sequence
# and are deliberately excluded from the prerequisites structure check.
DEDICATED_ENERGY_CONTROL_DOCUMENTS = (
    "hydraulic-press-lockout-tagout.md",
    "hydraulic-press-energy-control.md",
)

# Documents that must be covered by the structural check. The tenant-alpha
# gearmotor and conveyor maintenance procedure was added here when its heading
# was normalized from "Energy isolation for this conveyor" to
# "## Safety prerequisites"; the tenant-beta document already used the
# standardized heading.
SAFETY_PREREQUISITES_REQUIRED = {
    "tenant-alpha": ("gearmotor-and-conveyor-maintenance.md",),
    "tenant-beta": ("gearmotor-and-conveyor-maintenance.md",),
}


def test_safety_prerequisites_structure():
    """Every applicable maintenance/diagnostic procedure must have ## Safety prerequisites followed by numbered list."""
    section_pattern = re.compile(
        rf"^{re.escape(SAFETY_PREREQUISITES_HEADING)}[ \t]*$.*?(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    # "1. item" is the required shape; any other valid numbered start also passes.
    numbered_item = re.compile(r"^[ \t]*\d+\.[ \t]+\S", re.MULTILINE)
    # Bullet syntax inside the section is rejected. Wrapped continuation lines of
    # a numbered item are indented plain text and are not matched here.
    bullet_item = re.compile(r"^[ \t]*[-*+][ \t]+\S", re.MULTILINE)

    checked: dict[str, list[str]] = {tenant: [] for tenant in TENANTS}
    for tenant in TENANTS:
        for path in documents_of(tenant):
            name = path.name
            if name in DEDICATED_ENERGY_CONTROL_DOCUMENTS:
                continue
            text = path.read_text(encoding="utf-8")
            match = section_pattern.search(text)
            if match is None:
                continue
            section = match.group(0)
            where = f"{tenant}/{name}"
            assert numbered_item.search(section), (
                f"{where}: '## Safety prerequisites' has no numbered list item"
            )
            bullets = bullet_item.findall(section)
            assert not bullets, (
                f"{where}: '## Safety prerequisites' contains bullet items "
                f"instead of numbered ones: {bullets}"
            )
            checked[tenant].append(name)

    for tenant, names in SAFETY_PREREQUISITES_REQUIRED.items():
        for name in names:
            assert name in checked[tenant], (
                f"{tenant}/{name} must be covered by the "
                f"'## Safety prerequisites' structure check"
            )
    assert checked["tenant-alpha"] and checked["tenant-beta"]