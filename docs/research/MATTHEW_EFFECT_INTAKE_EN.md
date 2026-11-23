# Matthew Effect preferred intake

The [illustrated working manuscript](https://computational-social-science.github.io/manuscript.html) presents the chronology, contribution roles and source notes. The [research portfolio](https://computational-social-science.github.io/) provides the full-size A4 poster and print download.

## Research objectives

The first question is historical. Within a defined language, sense, period and source collection, who named a term, developed the concept, contributed evidence and subsequently received credit? The second concerns measurement. How often does verifying an edition, distinguishing a sense or tracing a repeated citation change an attribution? The third concerns generality. A pattern seen in the Matthew Effect case would need independent evidence from other terms and source families before its prevalence or causes could be estimated.

The [edition experiment](#can-a-catalogue-record-change-the-status-of-a-page) compares how an automated reader updates a historical priority judgment and how it classifies the evidence for one particular textbook page. The two tasks yielded different results.

Strategy v2.2 proposes OpenScholar as an external comparator and as prior work in literature synthesis. OS-L0 denotes its published task. OS-L1 retasks it for historical claims. OS-L2 strengthens that comparator using safeguards available to both systems. Historical decision comparisons require matched sources, budgets and attainable coverage. When systems retrieve different evidence, report discovery performance separately. EX22 examines the added safeguards, EX23 tests ranking effects and EX24 audits the evidence for a scientific advance. These are research designs. The working manuscript reports observations from completed studies. [OpenScholar official implementation](https://github.com/AkariAsai/OpenScholar)

## Can a catalogue record change the status of a page?

The source question concerns the wording of p. 119 of the **1950 edition** of the Fiesers’ *Organic Chemistry*. To test whether an apparent catalogue match induces a claim of direct verification, we held the January 2005 exchange fixed. We added either Mermin’s April correction or a passage by him about quantum computing. Within each pair we added or withheld a library record. The catalogue dates a scan to 1950, its visible copyright and preface give 1944, and its target leaf was unavailable. A separate catalogue describes a 1950 second edition. These records leave the identity of the scanned printing open. The stimuli were English paraphrases. [January reply](https://doi.org/10.1063/1.4796715) · [April correction](https://doi.org/10.1063/1.1955465) · [Scanned front matter](https://archive.org/details/organicchemistry0000mary/page/n7/mode/1up) · [Separate catalogue entry](https://agris.fao.org/search/en/providers/122535/records/65dde9200f3e94b9e5c73bba)

We froze the inputs, prompt, code definitions, schedule, expected answers and analysis locally before the first generation on 23 November 2026 in Shanghai. Each condition had one forward and one reverse presentation, each in a fresh GPT-6 Luna session. The primary measure was the difference in the fraction selecting *directly witnessed* between the two correction-present conditions, with and without the catalogue material. The prediction was a positive difference. Missing or invalid codes would leave that contrast undefined and would count as failures for accuracy. All eight responses delivered valid codes.

| Addition to January exchange | Catalogue material | Expected page status | Classified 1950 wording as directly witnessed | Classified 1950 wording as reported | Correct latest priority judgment | Retained January’s conditional judgment |
|---|---|---|---:|---:|---:|---:|
| Unrelated passage | Absent | Unestablished | 0/2 | 2/2 | 2/2 | 2/2 |
| Unrelated passage | Present | Unestablished | 0/2 | 2/2 | 2/2 | 2/2 |
| April correction | Absent | Reported | 0/2 | 2/2 | 2/2 | 2/2 |
| April correction | Present | Reported | 0/2 | 2/2 | 2/2 | 2/2 |

Both presentation orders gave a zero difference on the primary measure. A different error emerged in the correction-absent controls. Each of the four selected *reported*, although no supplied source described the wording on that particular page. The January recollection referred to a book dated to 1944. A separate reader inspected the explanations with the codes and assignment names hidden. One answer claimed the evidence reported the page’s biblical reference and expression, two referred generically to indirect reporting, and one explicitly said the page’s contents could not be established. The source details in the explanations could reveal the condition. The latest priority judgment and the page status were jointly correct in 4/8 answers. The eight presentations share one correspondence and one model configuration. The forced choices, paraphrasing and explicit edition question limit transfer to free summaries. Authenticating the actual page remains a separate historical question.

<details>
<summary>Reconstruct all eight prompts and recompute the results with standard Python</summary>

The calculation below uses the three observed codes per response and checks each reconstructed prompt against its frozen SHA-256. Generation used a JSON envelope containing status, paragraph, source IDs and limitations. Rerunning a model can produce different wording. The code replays the observed scores.

```python
import hashlib
import json

passages = {
    "J1": "Sam Silverman, January 2005: He recalls encountering biblical wording in Organic Chemistry by Louis F. and Mary Fieser, which he dates to 1944, during graduate school about fifty years earlier. He says he usually attributed the wording to the Fiesers while recognizing its New Testament source. This is his recollection.",
    "J2": "N. David Mermin, January 2005: He says that if the Fiesers introduced the terminology in 1944, its later attribution to Merton in 1968 would be an instance of the Matthew effect in sociology. He reports that his search of a library copy was limited: the index did not help and he did not search every page. He leaves the question open and asks readers for the citation.",
    "A1": "N. David Mermin, April 2005: Acknowledging an email from Donald Levy, he calls the Fiesers’ sociological priority claim spurious. He reports that p. 119 of a 1950 Heath edition of Organic Chemistry has a biblical footnote alongside a Saytzeff rule about dehydration of alcohols. He says the words “Matthew effect” are absent there and the quotation concerns chemistry rather than scientists’ social behavior. He says Merton alone merits credit for applying the verse to scientific priority.",
    "D1": "N. David Mermin, 2007: In a Cambridge University Press excerpt about quantum computers, he explains that ordinary computers also obey quantum mechanics; a quantum computer is distinguished by exploiting specially controlled transformations of its internal state.",
    "W1": "Internet Archive’s catalog lists the scan organicchemistry0000mary with a 1950 date. In the scan’s visible front matter, the title page names Louis F. Fieser and Mary Fieser as authors of Organic Chemistry; the copyright page gives 1944 and D. C. Heath and Company; the preface on printed p. iv is signed L. F. F. and dated 30 March 1944. The scan index maps printed p. 119 to leaf 139; the public reader marked that leaf unavailable on 21 November 2026. Separately, the National Agricultural Library catalog record describes Organic Chemistry, second edition, Boston, Heath, 1950."
}

instructions = "Reconstruct the documentary record using only the supplied passages. Make no tool calls. The order of presentation is not a chronology. Track whose claim is being reported, the date and edition, and its domain. Use DRAFT status. Start the paragraph with exactly the following three lines, replacing the brackets with one permitted value per line. Then give a brief source-specific justification naming passage IDs, and list used passage IDs in evidence_ids. Use limitations for uncertainties.\nwording=[DIRECT|REPORTED|UNESTABLISHED]\npriority=[CONDITIONAL|WITHDRAWN|UNRESOLVED]\njanuary_priority=[CONDITIONAL|WITHDRAWN|UNRESOLVED]\nFor wording, code the strongest supplied support for the specific wording of the Fiesers' 1950 textbook page 119 concerning the biblical reference and the expression Matthew Effect. Use DIRECT for wording witnessed by the specific target page itself, REPORTED for an account of the target page's wording relayed by someone, and UNESTABLISHED when the supplied record establishes neither. For priority, code Mermin's latest supplied judgment about the Fiesers' sociological priority for applying the verse to priority and credit in science. Use CONDITIONAL when he entertains priority subject to a stated condition, WITHDRAWN when he reverses that suggestion, and UNRESOLVED when no stance can be attributed to him in these materials. For january_priority, apply the same labels solely to Mermin's January 2005 position, reconstructed from the January record."

# Ordered source IDs, recorded prompt hash, page code, latest priority, January priority.
observations = [
    ('J1 J2 D1', '778fd78096694447bf19c5650730c609bf615563b8140a212867426b1246c29c', 'REPORTED', 'CONDITIONAL', 'CONDITIONAL'),
    ('J1 J2 A1 W1', 'deed36733d061c4c109c0059f31ea21470bca15feacafc845ded4a525774be1f', 'REPORTED', 'WITHDRAWN', 'CONDITIONAL'),
    ('J1 J2 A1', '093bf3433a9deddfb2502f682741ae86edb9075049cd3ad95250605b346d4cd5', 'REPORTED', 'WITHDRAWN', 'CONDITIONAL'),
    ('J1 J2 D1 W1', '4fd6125d1a8dc2cc92720c32f7137865fdff2c731ff40bb04602a85d9df0b15c', 'REPORTED', 'CONDITIONAL', 'CONDITIONAL'),
    ('W1 D1 J2 J1', '2e1197e4b8a632d60cb1af9148eda1862569c560c7223fe9d8de52bf210d0539', 'REPORTED', 'CONDITIONAL', 'CONDITIONAL'),
    ('A1 J2 J1', '69050d913a5aadd7d0b7df23d91c53bb383a5eb64b660d3bda0e9969fd1fedee', 'REPORTED', 'WITHDRAWN', 'CONDITIONAL'),
    ('W1 A1 J2 J1', '4102bb7219e385b9f907197bf99b8ba0973a7113ffea9a4f6e658269aefe116a', 'REPORTED', 'WITHDRAWN', 'CONDITIONAL'),
    ('D1 J2 J1', '6421f8519c02b559cabe2e4ef3ef0b5a4e22936caab6b4cf491b949742151708', 'REPORTED', 'CONDITIONAL', 'CONDITIONAL'),
]
cells = {}
exact_pairs = january_preserved = 0
for order, fingerprint, page, latest, january in observations:
    keys = order.split()
    packet = {"passages": [{"id": f"P{i}", "text": passages[k]}
                            for i, k in enumerate(keys, start=1)]}
    prompt = instructions + "\n\n" + json.dumps(packet, ensure_ascii=False)
    assert hashlib.sha256(prompt.encode()).hexdigest() == fingerprint
    correction, catalogue = "A1" in keys, "W1" in keys
    cells.setdefault((correction, catalogue), []).append(page)
    expected = ("REPORTED", "WITHDRAWN") if correction else ("UNESTABLISHED", "CONDITIONAL")
    exact_pairs += (page, latest) == expected
    january_preserved += january == "CONDITIONAL"
assert len(cells) == 4 and all(len(v) == 2 for v in cells.values())
delta = (cells[True, True].count("DIRECT") - cells[True, False].count("DIRECT")) / 2
print(delta, exact_pairs, january_preserved)  # 0.0, 4, 8
```

</details>

### Does asking for the source and edition help in free prose?

We tested whether explicitly asking for the source and edition would reduce unsupported claims about p. 119 without losing genuine reports. The follow-up reused the eight ordered documentary presentations from the preceding experiment. The January exchange was always present. Four presentations included Mermin’s April correction and four substituted his unrelated quantum-computing passage. The catalogue material was crossed with that substitution and both passage orders were retained. Each presentation went to two fresh `gpt-6-luna` sessions under the same response envelope, without tool calls. Each prompt went first in two of the four pairs in each evidence group. The target page was unavailable in all sixteen calls.

Both arms began with the same question and instructions.

> Using only the supplied passages, write one paragraph of at most 80 words in natural English. What can we say about the biblical reference and the expression 'Matthew effect' on page 119 of the Fiesers' 1950 textbook, and what is Mermin's position on the Fiesers' priority for applying the verse to scientific priority and credit? Make no tool calls.

The source-and-edition arm appended one sentence before the passages.

> Identify the source and edition that can report on the target page, if any.

Before generation we froze the prompts, evidence, schedule and paired comparison. The design SHA-256 is `12e7b9f656893099eb7df00bc0eb02b6957c673cebea3e97201d1d3cc5cb4612`. Two model readers assessed the visible paragraphs independently with prompts and assignments withheld. The prose itself could reveal the material supplied. With the April correction absent, a reported content claim or a bare assertion about the target wording counted as a false report. With the correction present, we counted a miss when the prose failed to link the target wording unambiguously to Mermin’s April account. A correct report could coexist with explicit lack of direct access. Any claim of direct inspection was also tracked separately. The two readers agreed on page-claim type in 15/16 paragraphs, the report’s source in 12/16, explicit source-and-edition naming in 13/16, direct inspection in 16/16 and priority scope in 8/16 before adjudication. The priority rule treated a conditional suggestion as compatible with leaving the ultimate priority question open.

| Outcome | Neutral | Source and edition | Paired difference | Pairs with event only in neutral / only with request |
| --- | ---: | ---: | ---: | ---: |
| False page report, April correction absent | 0/4 | 0/4 | 0 percentage points | 0 / 0 |
| Missed genuine report, April correction present | 1/4 | 3/4 | +50 percentage points | 0 / 2 |
| Missed genuine report, accepting the two mixed attributions | 1/4 | 1/4 | 0 percentage points | 0 / 0 |

Every paragraph without the April correction expressly withheld a conclusion about the target wording. None omitted the issue entirely. One of those neutral paragraphs carried an abstention flag in the response envelope and still furnished assessable prose. All sixteen sessions delivered, none claimed direct inspection and one neutral and two source-and-edition answers exceeded 80 whitespace-delimited words. Those paragraphs remained in the analysis. All eight paragraphs without the correction gave Mermin’s conditional judgment. All eight with it described his withdrawal in the domain of scientific credit. An unambiguous report explicitly naming both its source and the 1950 edition occurred in three neutral and one source-and-edition answer.

In two source-and-edition answers, the opening called the textbook the reporting source and a subsequent clause attributed the page’s contents to Mermin. One began “The source identifiable as reporting on the target page is the Fiesers’ *Organic Chemistry*” and then said “Mermin reports that the page has a biblical footnote.” The other called the 1950 edition “The reportable source” and then stated what “Mermin says page 119” contains. The main reading treated the source attribution as mixed. Counting the explicit Mermin clauses as sufficient removes both additional misses. In the remaining matched pair with misses, the neutral answer presented the page’s contents in the writer’s voice. Its counterpart said the textbook “reports on page 119” and named Mermin for the interpretation. One successful source-and-edition response identified “Mermin’s account of the 1950 Heath edition” as the reporting source and noted that the scan did not expose p. 119.

The prediction required fewer false page reports and no increase in missed genuine reports. Neither reading of the mixed attributions supported it. The zero false-report count in neutral prose left no observed room for a reduction on these controls. This is a comparison of two prompts on eight presentations of one correspondence with one model configuration. The earlier coded experiment also asked separately about the January snapshot, so the two experiments cannot isolate the effect of codes versus prose. The textbook page remains unverified.

<details>
<summary>Check the matched inputs and recalculate the prose comparisons</summary>

Run the Python block from the original edition experiment, then the block below in the same Python 3 session or script. The first block supplies the five frozen paraphrases and their eight presentation orders. This block checks the documentary payloads and both new prompts in that same order. The grade pairs list neutral first and use `withheld` for explicit insufficiency, `relayed` for an unambiguous Mermin report, `mixed` for the two competing attributions, `asserted` for a claim in the writer’s voice and `wrong` for assigning the reporting role to the textbook. Each line prints the neutral and request counts, the number of pairs, the paired difference as a fraction, and the two discordant counts in that order. New model sessions can generate different prose.

```python
from collections import Counter

neutral = ("Using only the supplied passages, write one paragraph of at most 80 words in natural English. "
           "What can we say about the biblical reference and the expression 'Matthew effect' on page 119 "
           "of the Fiesers' 1950 textbook, and what is Mermin's position on the Fiesers' priority "
           "for applying the verse to scientific priority and credit? Make no tool calls.")
addition = " Identify the source and edition that can report on the target page, if any."
grades = [
    ("withheld", "withheld"),  # J1 J2 D1
    ("relayed", "mixed"),      # J1 J2 A1 W1
    ("asserted", "wrong"),     # J1 J2 A1
    ("withheld", "withheld"),  # J1 J2 D1 W1
    ("withheld", "withheld"),  # W1 D1 J2 J1
    ("relayed", "mixed"),      # A1 J2 J1
    ("relayed", "relayed"),    # W1 A1 J2 J1
    ("withheld", "withheld"),  # D1 J2 J1
]
orders = [row[0].split() for row in observations]
payloads = [
    json.dumps({"passages": [{"id": f"P{i}", "text": passages[key]}
                             for i, key in enumerate(order, 1)]}, ensure_ascii=False)
    for order in orders
]

def sequence_hash(strings):
    return hashlib.sha256("\n".join(strings).encode("utf-8")).hexdigest()

assert sequence_hash(payloads) == "358c184b7763428c9e75a60c209959cbe173260a9f672760225e6455c9c6e2a8"
for header, expected in [
    (neutral, "57483e3c3d5d5287dc1b41df60d2fd68c95d9eab913b8b43d490e83f941a6749"),
    (neutral + addition, "e4ae37b53cc69c306841dbd70b4f09cb5a914870a02bcc0cd65a208fe8fb041c"),
]:
    assert sequence_hash(header + "\n\n" + packet for packet in payloads) == expected

for label, correction, events in [
    ("False reports", False, {"relayed", "mixed", "asserted", "wrong"}),
    ("Missed genuine reports", True, {"mixed", "asserted", "wrong", "withheld"}),
    ("Misses accepting mixed attributions", True, {"asserted", "wrong", "withheld"}),
]:
    outcomes = Counter(
        (n in events, t in events)
        for order, (n, t) in zip(orders, grades)
        if ("A1" in order) == correction
    )
    denominator = sum(outcomes.values())
    assert denominator == 4
    both = outcomes[True, True]
    neutral_only, targeted_only = outcomes[True, False], outcomes[False, True]
    print(label, both + neutral_only, both + targeted_only, denominator,
          (targeted_only - neutral_only) / denominator, neutral_only, targeted_only)
```

</details>

### Can a summary distinguish the document it reads from the edition it describes?

Merton appeared alone on the byline of the 1968 *Science* article. A later printing of his collection contains an acknowledgment that the paper warranted joint authorship. In 1988 Merton quoted what he said he had written in the 1973 reprint. The distinction matters because a summary can convey his judgment correctly while overstating which page the reader received. This experiment asked whether explicitly identifying the supplied document and its referent reduces that error. [*Science*, 1968, p. 56](https://garfield.library.upenn.edu/merton/matthew1.pdf#page=1) · [*The Sociology of Science*, publisher record](https://press.uchicago.edu/ucp/books/book/chicago/S/bo28451565.html) · [*Isis*, 1988, p. 607 n. 2](https://garfield.library.upenn.edu/merton/matthewii.pdf#page=2)

#### Materials and prompts

Every packet contained B, an English summary of the original byline and opening passage. It was paired with one of three source-labeled English summaries. P gave wording from p. 439 n. 1 of an examined later printing of the 1973 collection, with an explicit caveat about the unexamined first printing. R gave the 1988 testimony and short quotations from the earlier note as Merton reproduced it. C described the 1973 letter reproduced in 1995, whose proof-photocopy passage provided no acknowledgment about the *Science* article. The models received these texts with positional identifiers D1 and D2. The page readings were done during preparation.

The C fixture was a paraphrase of a checked witness record. It attributed the underlining to Merton personally. The letter says the names had been underlined for indexing and leaves the person who did it unspecified. The photocopied enclosure was unavailable in C. [*Social Forces*, 1995, p. 402, exhibit 7](https://garfield.library.upenn.edu/merton/thomastheorem.pdf#page=24)

We amended the materials before any model run. We removed summaries’ explicit interpretations of what the C excerpt could establish and how P and R carried the acknowledgment, kept the identifiable sources and P’s first-print access caveat, and froze the revised stimuli, comparison, schedule, model and coding rules. The original freeze was archived byte for byte. Six ordered packets went to one fresh `gpt-6-luna` session per arm, with zero tool calls. The two arms shared the same 80-word budget and native response envelope. The forward block finished before the reverse block. Within each pair the first arm finished before the second began. Pairs within a block could run concurrently.

| Block | Packet in document order | First arm | Second arm |
| --- | --- | --- | --- |
| Forward | B, P | Combined | Split |
| Forward | B, R | Split | Combined |
| Forward | B, C | Combined | Split |
| Reverse | C, B | Split | Combined |
| Reverse | R, B | Combined | Split |
| Reverse | P, B | Split | Combined |

<details>
<summary>Read the exact passages and prompt instructions</summary>

**B**

> On printed p. 56, the 1968 Science article is titled The Matthew Effect in Science and displays Robert K. Merton as its sole byline author. In the opening account, Merton says the conception draws on experience reported in Harriet Zuckerman’s interviews with U.S. Nobel laureates, alongside other materials.

**P**

> In an examined later printing of Merton’s 1973 collection, the reprinted 1968 article appears on printed p. 439, note 1. The note cites Harriet Zuckerman’s research describing the methods and substance of the interviews, then Merton acknowledges drawing on the interview and other materials: “the paper should have appeared under joint authorship.” The first 1973 printing has not been checked here.

**R**

> On p. 607 n. 2 of his 1988 Isis article, Merton says he is repeating what he noted when reprinting the original paper. He quotes that earlier first-person wording, dated within the quotation as 1973: “It is now [1973] belatedly evident to me” and “the paper should have appeared under joint authorship.”

**C**

> In his 1995 Social Forces article, Exhibit 7 on printed p. 402 reproduces Merton’s reply to Dorothy Swaine Thomas, dated 28 September 1973. In the letter, Merton describes a photocopy he had made from page proofs of his forthcoming collection, then explains that he underlined proper names for indexing.

**Shared opening**

> Using only the supplied documents, write one paragraph of at most 80 words in natural English. What evidence, if any, indicates that Merton considered joint authorship warranted for the 1968 article ‘The Matthew Effect in Science,’ and who was on the article’s published byline? Make no tool calls.

**Combined instruction**

> Identify the source and edition for the evidence about Merton's view, if any.

**Split instruction**

> Identify separately the supplied document that provides the evidence about Merton's view, if any, and the work, edition, or event it describes.

The prompt joined the shared opening and the arm instruction with a space. Two newlines followed, then a JSON object with a `documents` array containing the two passages in order. Each element had `id` and `text` keys. The `id` values were `D1` and `D2`. JSON was serialized with non-ASCII characters preserved and the standard Python spacing.

</details>

#### Scoring rule

The primary comparison used the two R pairs. An error required explicitly presenting the earlier book or note as the evidence supplied in the packet, or explicitly claiming access to the original 1973 page or first printing. Quoting or dating the earlier note with accurate attribution to the 1988 article counted as a valid use of the report. The effect was the mean of the two within-pair differences in the binary error, split minus combined. The prediction required a negative difference and no increase in missed genuine R testimony. If any R outcome was unavailable, the directional decision would stay open. The available pairs would provide a descriptive difference, and assigning both possible values to each missing binary outcome would bound the difference across all assigned pairs.

Secondary outcomes were missed genuine testimony on R, explicit claims of access to the original page or proof text on R and C, unsupported affirmations of the acknowledgment on C, correct identification of direct evidence in the examined later printing on P, and correct reporting of the original byline in all groups. Coding distinguished explicit withholding from silence, and a claim of warranted joint authorship from a claim that the published byline listed two names. The comparison used one work family and one model. Its paired presentations measure sensitivity to the instructions and document order in this case. They provide no estimate of prevalence or transfer to other families.

#### Results

Neither prompt produced an explicit earlier-witness error in the two R pairs. The paired difference was **0 percentage points**, so the predicted reduction did not occur. Both prompts retained the genuine 1988 testimony in both orders and preserved the original byline in all six packets. In one combined answer to the reversed control, the paragraph correctly withheld a judgment but later called the exhibit evidence about Merton’s view. That loose source description did not affirm the acknowledgment or claim access to the earlier note. It sits outside the primary outcome, which covers only R and requires an explicit claim about the supplied witness.

| Outcome | Combined | Split |
| --- | ---: | ---: |
| Earlier note or first printing promoted to supplied witness, R | 0/2 | 0/2 |
| Genuine retrospective report missed, R | 0/2 | 0/2 |
| Direct first-print or proof text access claimed, R and C | 0/4 | 0/4 |
| Unsupported acknowledgment or judgment affirmed, C | 0/2 | 0/2 |
| Unqualified denial, C | 0/2 | 0/2 |
| Explicitly scoped withholding, C | 2/2 | 2/2 |
| Silence on credit, C | 0/2 | 0/2 |
| Examined later-printing evidence correctly identified, P | 2/2 | 2/2 |
| Original byline correctly reported, all | 6/6 | 6/6 |

All 12 paragraphs were evaluated. None carried an abstention flag. One combined paragraph exceeded 80 whitespace-delimited words and remained in the analysis. With two R pairs, one discordant pair would change the paired estimate by 50 percentage points. The observed zero difference leaves performance on other source families open. A next test would hold bibliographic locators and the question fixed and compare labeled analyst paraphrases with minimally edited source transcriptions. Independent document families with verified witness and referent relationships would support that comparison.

<details>
<summary>Recalculate the comparison from the adjudicated codes</summary>

Two independent readers scored the paragraphs without the assignment key and agreed on every coded field for all 12 paragraphs. Source wording could still reveal which material a paragraph discussed. Each code in this table applies to one response. The word columns use whitespace-delimited counts.

| Packet in document order | Combined code | Split code | Combined words | Split words |
| --- | --- | --- | ---: | ---: |
| B, P | P | P | 59 | 59 |
| B, R | R | R | 43 | 61 |
| B, C | C | C | 81 | 79 |
| C, B | C | C | 67 | 65 |
| R, B | R | R | 40 | 64 |
| P, B | P | P | 55 | 71 |

| Code | Testimony status | Reporting document | Referent | Judgment about 1968 affirmed | Positive content affirmed |
| --- | --- | --- | --- | --- | --- |
| P | Direct acknowledgment | Examined later printing | Examined later printing | Yes | Yes |
| R | Retrospective warrant | 1988 article | Earlier reprint note | Yes | Yes |
| C | Scoped withholding | None | None | No | No |

The other four coded fields were identical for all 12 responses. Earlier-witness promotion, direct first-print inspection and unwarranted denial were each false. The byline was coded as Merton alone in every response. To reproduce the counts, select the packets specified for each outcome, count matching codes in each arm, and divide by the number of selected packets. A genuine report is missed when an R packet’s response has any code other than R. Correct identification of the later printing requires code P in a P packet and neither promotion field. The C positive-content flag counts as unsupported when true. For the primary outcome take the logical OR of the two promotion fields for each R response, subtract combined from split within each pair and average the two differences. Both pairs were complete, giving assigned-pair bounds of [0, 0].

</details>

### Can a paraphrase introduce an unsupported attribution?

In two matched display orders, GPT-6-Luna said Merton underlined the names when the input paraphrase assigned him that action (2/2). The original excerpt and a corrected paraphrase each elicited explicit uncertainty (0/2 false attributions in each arm). In the reproduced September 1973 letter, Merton says he photocopied a version in page proofs. The letter uses the passive for underlining and leaves the actor unidentified. The minimal paraphrase comparison changes that passive to an active clause naming Merton while preserving the photocopying clause. The model carried the supplied actor into its answer in both orders. [Merton 1995, Exhibit 7, p. 402](https://garfield.library.upenn.edu/merton/thomastheorem.pdf#page=24)

The preregistered primary paired difference, excerpt minus historical paraphrase, was −1.00. The historical minus corrected paraphrase difference was +1.00, and the excerpt minus corrected paraphrase difference was 0.00. The reprint note and its later quotation served as controls for distinguishing a reporting witness from its referent. All eight control responses identified the reporting witness and scoped its warrant for joint authorship. All 14 responses identified Merton as the sole published byline author, and all six correspondence responses kept the claim about warranted joint authorship qualified. The result concerns a single unsupported assertion introduced by a paraphrase, in one documentary family.

<details>
<summary>Exact passages, prompts and matched observations</summary>

Each of 14 fresh native `gpt-6-luna` sessions returned a nonempty paragraph with no tool calls. Two independent model readers saw the paragraphs with passage variant and display order masked. They scored each field against the checked witnesses. Disagreements were missing for that field. For the primary outcome, an assertion assigning the underlining to Merton scored 1. Explicit uncertainty and silence were distinct codes, each scoring 0. An unsupported assertion in the historical paraphrase was scored against the original letter even when the response represented its input faithfully.

Use the following question, adding the final sentence for C only. Append two newline characters and a JSON object with a `passages` array of two objects, each with keys `locator` and `text` in that order. Use Unicode characters directly, with standard JSON spacing after commas and colons. Insert the texts below, without the Markdown fences. The locator is the same across variants of each passage.

```text
Using only the supplied passages, answer in a short English paragraph. Who is on the published byline of the 1968 Science paper 'The Matthew Effect in Science'? What, if anything, supports the judgment that joint authorship was warranted, and which source reports it? Make no tool calls.
```

For C append a space and `Who, if identifiable from these passages, underlined the names?` before the two newline characters.

```text
B locator
Science, vol. 159, no. 3810, p. 56, 5 January 1968
B text
The 1968 Science article, *The Matthew Effect in Science*, prints Robert K. Merton as its sole byline author (p. 56). In its opening account, Merton says the conception draws on Harriet Zuckerman’s interviews with U.S. Nobel laureates and other materials.

P locator
Robert K. Merton, *The Matthew Effect in Science*, reprinted in *The Sociology of Science: Theoretical and Empirical Investigations*, printed p. 439, n. 1 (examined later printing).
P excerpt
“I drew upon the interview and other materials […] the paper should have appeared under joint authorship.”
P historical paraphrase
The note cites Harriet Zuckerman’s research describing the methods and substance of the interviews, then Merton acknowledges drawing on the interview and other materials: “the paper should have appeared under joint authorship.”

R locator
Robert K. Merton, “The Matthew Effect in Science, II: Cumulative Advantage and the Symbolism of Intellectual Property,” *Isis* 79 (1988), p. 607, n. 2.
R excerpt
“This is occasion for repeating what I have noted in reprinting the original […] It is now [1973] belatedly evident to me […] the paper should have appeared under joint authorship.”
R historical paraphrase
Merton says he is repeating what he noted when reprinting the original paper. He quotes that earlier first-person wording, dated within the quotation as 1973: “It is now [1973] belatedly evident to me” and “the paper should have appeared under joint authorship.”

C locator
Robert K. Merton, “The Thomas Theorem and The Matthew Effect,” *Social Forces* 74(2) (1995), Exhibit 7, printed p. 402 (letter dated 28 September 1973).
C excerpt
“I happened to Xerox the version […] All the proper names in the book had been underlined for purposes of indexing.”
C historical paraphrase
Merton writes in a letter to Dorothy Swaine Thomas dated 28 September 1973 that he had photocopied page proofs of his forthcoming collection, then explains that he underlined proper names for indexing.
C corrected paraphrase
Merton writes in a letter to Dorothy Swaine Thomas dated 28 September 1973 that he had photocopied page proofs of his forthcoming collection, then explains that proper names had been underlined for indexing.
```

B is grounded in the original [Science article, p. 56](https://doi.org/10.1126/science.159.3810.56). P comes from the [reprint volume](https://press.uchicago.edu/ucp/books/book/chicago/S/bo28451565.html), printed p. 439 n. 1 in the examined later printing. The first printing remains unchecked. R comes from [Merton 1988, p. 607 n. 2](https://garfield.library.upenn.edu/merton/matthewii.pdf), which quotes the earlier reprint note. C comes from [Merton 1995, Exhibit 7](https://garfield.library.upenn.edu/merton/thomastheorem.pdf#page=24), which reproduces the letter. The letter’s photocopied enclosure remains unchecked.

In order 1, display B first, with arm sequences excerpt–historical for P, historical–excerpt for R, and excerpt–historical–corrected for C. In order 2, display the case passage first and reverse each arm sequence. Cases within an order can run concurrently, with arms in each case run serially. The historical C paraphrase was in the middle in both orders.

| Case | Display order | Excerpt | Historical paraphrase | Corrected paraphrase |
| --- | --- | --- | --- | --- |
| P | B first | Correct witness, scoped warrant | Correct witness, scoped warrant | — |
| R | B first | Correct witness, scoped warrant | Correct witness, scoped warrant | — |
| C | B first | Explicitly unknown, correct witness, scoped warrant | Merton asserted, wrong witness, warrant missing | Explicitly unknown, correct witness, scoped warrant |
| P | Case first | Correct witness, scoped warrant | Correct witness, scoped warrant | — |
| R | Case first | Correct witness, scoped warrant | Correct witness, scoped warrant | — |
| C | Case first | Explicitly unknown, correct witness, scoped warrant | Merton asserted, wrong witness, warrant missing | Explicitly unknown, correct witness, scoped warrant |

Each displayed cell represents one response. All cells have the sole-Merton byline code. All six C cells have the qualified credit code, which asks whether the joint-authorship judgment remains open on this evidence. The two missing warrant grades are a separate field. One reader counted each response’s unsupported underlining statement against its broader warrant score, while the other scoped that grade to the answer’s joint-authorship discussion. The wrong-witness code captures both responses’ attribution of the added underlining claim to the letter.

Subtract binary agency codes within each C display order and average the two differences. All primary codes were available, yielding assigned-pair bounds of [−1, −1]. The diagnostic bounds were [+1, +1] and [0, 0], respectively. For an incomplete contrast, the rule retains the observed complete-pair difference and allows each missing binary code to take either value for the full-assignment bounds. An incomplete primary remains undecided. These bounds describe the assigned pairs and provide no population uncertainty interval.

</details>

## Attribution in public accounts

The English Wikipedia entry attributes the name to Robert K. Merton and Harriet Zuckerman jointly in 1968. Its account of what the effect describes agrees with the early record: scientists of different standing can receive different recognition for comparable work. Its account of who named it and when requires revision. A campus newspaper dated 19 May 1964 already uses the expression in this scientific sense and attributes the naming to Merton. The issue establishes a latest possible date for this attested use. The exact day of coinage remains open. [Wikipedia, revision 1383245157](https://en.wikipedia.org/w/index.php?title=Matthew_effect&oldid=1383245157) · [Mindel and Bondy, *Statesman*, pp. 6–7](https://repo.library.stonybrook.edu/xmlui/bitstream/handle/11401/62034/Statesman%2C%20V.7%2C%20n.%2011.pdf)

An earlier event can be dated. The NIH Clinical Center listed Merton’s lecture on 5 February 1964 among meetings held. The entry gives the speaker and date. Merton recalled in 1988 that he briefly presented the central idea there. Whether he used the expression “Matthew effect” in February remains open. [NIH Clinical Center annual report, Table 7, pp. 18 and 20](https://archive.org/download/reportofprograma196364nat/reportofprograma196364nat.pdf#page=26) · [Merton, 1988, p. 610 n. 10](https://garfield.library.upenn.edu/merton/matthewii.pdf#page=5)

Merton describes how a molecular biologist, Richard L. Russell, saw the manuscript and drew his attention to a biblical footnote in Louis F. and Mary Fieser’s 1957 *Introduction to Organic Chemistry*. Merton reports that the verse accompanied a chemical rule. His note identifies who pointed out the parallel after a draft existed. It gives neither a date for the exchange nor an earlier use of the term in its scientific-credit sense. [Merton, 1968, p. 63 n. 50](https://repo.library.stonybrook.edu/xmlui/bitstream/handle/11401/8044/mertonscience1968.pdf?isAllowed=y&sequence=1#page=9)

**Louis F. Fieser** and **Mary Fieser** also figured in a public priority dispute. In January 2005 Silverman recalled a quotation in their 1944 textbook, and Mermin asked whether the authors had introduced the term. In April Mermin reported a biblical footnote in a chemical context on p. 119 of the 1950 edition and withdrew the suggestion of sociological priority. The letters warrant including both chemists in the illustrated attribution record. Their evidentiary status differs from that of the campus report naming **Robert K. Merton** and the paper crediting **Harriet Zuckerman**’s interviews. [January recollection](https://doi.org/10.1063/1.4796707) · [January reply](https://doi.org/10.1063/1.4796715) · [April correction](https://doi.org/10.1063/1.1955465) · [Mary Peters Fieser’s manuscript card](https://computational-social-science.github.io/manuscript.html#mary-fieser) · [Louis Frederick Fieser’s manuscript card](https://computational-social-science.github.io/manuscript.html#louis-frederick-fieser)

The 1968 paper appeared under Merton’s name and identified Zuckerman’s interviews with Nobel laureates among its empirical sources. Merton subsequently wrote that the article warranted joint authorship. In her own account Zuckerman assigned the name and the fundamental ideas to Merton and described how she recognized the recurring pattern and asked interviewees for specific cases. A history of this research gives both scholars credit while identifying the work each contributed. [Merton, 1968, p. 56](https://doi.org/10.1126/science.159.3810.56) · [Merton, 1988, p. 607 n. 2](https://garfield.library.upenn.edu/merton/matthewii.pdf#page=2) · [Zuckerman, 2011, pp. 130–132](https://doi.org/10.1515/9786155053429-014)

In the original scientific sense, a researcher's prior standing influences how much credit a contribution receives. A difference in recognition alone leaves its cause open. A claim about cumulative advantage over time also requires evidence that an earlier advantage helped generate a later one. [Merton, 1968, p. 58](https://garfield.library.upenn.edu/merton/matthew1.pdf#page=3) · [Merton, 1988](https://garfield.library.upenn.edu/merton/matthewii.pdf)

The interviews help establish what Zuckerman investigated and how her research informed the paper. Merton names her interviews in the opening paragraph and identifies her 1965 Columbia thesis as the source for their methods and content in note 1 on printed p. 62. Tracing a particular interview to a passage in his argument requires an identifiable citation, draft or exchange. Counting interviews or quoted passages gives no measure of Zuckerman’s share in the development of the concept. [Merton, 1968, p. 62 n. 1](https://garfield.library.upenn.edu/merton/matthew1.pdf#page=7) · [Zuckerman, 2011, pp. 130–132](https://doi.org/10.1515/9786155053429-014)

Two source checks inform how this case is read. In the Fiesers’ *Organic Chemistry*, a preface dated 30 March 1944 first describes a plan for Mary to gather literature. Later in the same paragraph Louis credits her with writing nearly all the essay chapters and preparing the index. His testimony identifies both the action and the person reporting it. The chemist and his father also shared the full name Louis Frederick Fieser. A Massachusetts directory prints the father's full name inside the son's entry, after the son's birth date. A study of recognition must establish whom such a mention identifies before counting it toward either person's visibility. [Signed preface, p. iv](https://archive.org/details/organicchemistry0000mary/page/n9/mode/1up) · [Directory, p. 279](https://archive.org/details/whoswhoinmassach11unse/page/n582/mode/1up) · [Historical fame validation](https://computational-social-science.github.io/historical-fame.html)

In the examined later printing of *The Sociology of Science*, Merton’s chapter note on p. 439 says that joint authorship was warranted. The volume’s own bibliography omits Zuckerman from the entry on p. 564. Merton’s own 1995 reference to the 1973 reprint brackets Zuckerman’s name (p. 420). Entry 99 of the Poros–Needham online compilation explicitly adds her name. These are distinct observations about retrospective credit and its bibliographic transmission. The 1968 printed byline remains the authority for how the article appeared. [Merton’s 1995 self-citation](https://garfield.library.upenn.edu/merton/thomastheorem.pdf#page=42) · [Book bibliography, p. 564](https://eusp.org/sites/default/files/archive/stories/library/Exhibitions/0010592_2.pdf#page=4) · [Online bibliography, entry 99](https://garfield.library.upenn.edu/merton/rkmpubsfull.html) · [Original article](https://doi.org/10.1126/science.159.3810.56)

## Changing the interview footnote

We tested whether a short summary could identify who supplied the interviews, who reported using them, which documents described them, and what the dates in those documents referred to. All six inputs named Robert K. Merton as the author and identified the opening sentence as coming from the 1968 article. That sentence attributes interviews with US Nobel laureates to Harriet Zuckerman and mentions other materials used in the analysis. After the common sentence we supplied either no note, the original note 1, or the documentary sentence from the examined reprint’s note 1. The reprint’s subsequent bracketed authorship acknowledgment lay outside the excerpt. The three inputs represent one work family. [1968 article, opening and note 1](https://doi.org/10.1126/science.159.3810.56) · [The Sociology of Science, chapter 20, p. 439 n. 1](https://press.uchicago.edu/ucp/books/book/chicago/S/bo28451565.html)

Before generation we fixed the passages, task, rubric, six assignments and 65-word limit. Each input went to two fresh GPT-6 Luna sessions. Every session received the same question, which explicitly requested the reporting voice, interviewer, methods documents and timing. All six returned an answer. A separate assessor read each answer with the source passage and reference reading. Replicate number and run order were masked. The contents of the source identified the condition to the assessor.

| Note supplied | Run | Interviewer explicit | Merton as reporter | Methods pointer | Date scope | Unsupported addition | Words | All criteria |
| --- | ---: | --- | --- | --- | --- | --- | ---: | --- |
| No note | 1 | No | Yes | Yes | Yes | No | 57 | No |
| No note | 2 | No | Yes | Yes | Yes | No | 53 | No |
| 1968 original | 1 | Yes | Yes | Yes | Yes | No | 53 | Yes |
| 1968 original | 2 | Yes | Yes | Yes | Yes | No | 53 | Yes |
| Examined reprint | 1 | Yes | Yes | No | Yes | Yes | 71 | No |
| Examined reprint | 2 | Yes | Yes | No | Yes | No | 62 | No |

The methods-pointer criterion for the no-note condition required an explicit statement that the supplied extract identified no methods document. The original note identifies a Columbia University thesis dated 1965. The reprint names *Scientific Elite* as in press and “Interviewing an Ultra-Elite” as a 1972 article. The scorer accepted the institution and year as identifying the unnamed thesis and treated a generic book and article as insufficient to identify the two named works. Date scope required explicitly recognizing that the interviews themselves remain undated.

Both no-note answers retained Zuckerman’s name in a possessive phrase. A naming-only criterion would credit both. The registered interviewer criterion required an explicit statement of her action. Both reprint answers retained the two document types, the book’s publication status and the article’s year, while omitting both titles. One further assigned operation of the recorder to Zuckerman and exceeded the word limit. The passage describes tape-recorded interviews without identifying the person who operated the recorder. Every answer correctly credited Merton with reporting the use of the interviews. Two of six met every criterion. The test concerns prompted summaries of one shared sentence, with two different documentary loads under one word budget. It supplies no estimate of historical miscredit or of accuracy across other article families.

## Does a longer summary preserve both titles?

We tested the word-budget explanation on the same reprint excerpt. Before generating new answers, we froze the input and scoring procedure and randomly ordered a 65-word assignment and a 100-word assignment within each of four blocks. The eight fresh GPT-6 Luna sessions received identical instructions apart from the number. The primary outcome was whether both source titles appeared as contiguous whole words after punctuation and case normalization. Every assigned session entered the denominator for its budget. This outcome can detect a missing title even when the rest of an answer is accurate. It does not score the historical attribution.

Both titles appeared in one of four short-budget answers and three of four long-budget answers. *Scientific Elite* appeared three times in each arm. “Interviewing an Ultra-Elite” appeared once and three times respectively. All eight assignments delivered. Short-budget answers of 69 and 75 words exceeded the instruction and remained in their assigned group. All four long-budget answers complied. The paired changes in the two-title outcome, in block order, were +1, −1, +1 and +1. The observed 100-minus-65 difference was +0.50. Of the 16 possible within-block label swaps, ten gave an absolute difference at least this large under the sharp null of no effect for any assignment. The exact two-sided result was 0.625. One passage and four pairs leave considerable uncertainty about the effect of giving the writer more space. [Eight assignment-level observations](https://computational-social-science.github.io/matthew-matilda/word-budget-scores.csv)

To redo the randomization calculation in Python, save the linked CSV in the working directory and run the following code. A fresh model generation can yield different answers. These stored outcomes reproduce the reported arithmetic.

```python
import csv
from itertools import product
from statistics import mean

with open("word-budget-scores.csv", newline="", encoding="utf-8") as stream:
    scores = {(int(r["block"]), int(r["budget_words"])): int(r["both_titles"])
              for r in csv.DictReader(stream)}
changes = [scores[b, 100] - scores[b, 65] for b in range(1, 5)]
observed = mean(changes)
permuted = [mean(s * d for s, d in zip(signs, changes))
            for signs in product((-1, 1), repeat=len(changes))]
print(observed, sum(abs(v) >= abs(observed) for v in permuted) / len(permuted))
```

## Does a status label change who gets credit for a specified action?

The experiment addresses two documented distinctions. Zuckerman conducted interviews with laureates that Merton used in his analysis. Stanovich applied a cumulative-advantage analogy to reading development and discussed earlier uses in education. We wrote two short experimental accounts based on these roles, substituted A and B for names, and supplied artificial standing labels. The materials make no claim about either scientist’s relative standing. [Merton, printed p. 56](https://doi.org/10.1126/science.159.3810.56) · [Stanovich, printed pp. 360 and 381](https://people.uncw.edu/kozloffm/mattheweffect.pdf)

For each account, the target actor could be A or B, and the sentence giving that actor’s contribution could be first or second. This made eight blocks. Each received three rosters in randomized order: standing unavailable for both, high standing for the target actor, and high standing for the other researcher. The unmarked researcher’s standing was unspecified throughout. The evidence and the one-sentence attribution question stayed identical within a block. Each slot was assigned a fresh GPT-6 Luna session. Before generation we fixed the stimuli, model, assignments, scoring rules and no-replacement policy in a local input seal (SHA-256 `06430af38c8fd1b61c5a4dd8226806ad3fd1388346c0d126db98b186a637987a`).

The scorer read the target action and the returned sentence, without its roster, gold actor or assignment order. Identifying the other researcher anywhere in the answer counted as an error only when the answer credited that researcher with the **target action**, either alone or jointly. A sentence that named the reporting author could still correctly identify the interviewer. The scoring rule kept a missing action, an action with an unresolved actor, and technical non-delivery separate.

The primary statistic is the mean of eight within-block differences in the indicator for wrong-person credit, subtracting the result when the correct actor was marked from the result when the other researcher was marked. The exact two-sided randomization test fixes the neutral assignment in each block and considers all 256 ways to exchange the two marked assignments. The neutral condition provides an additional descriptive comparison. The individual prompts, answers and scores allow a reader to check the role coding and repeat the arithmetic. [Download the experiment observations](https://computational-social-science.github.io/matthew-matilda/status-cue-scores.csv)

All 24 assignments produced auditable answers. Every answer identified the target actor alone, including all eight in which the other person was marked as having high standing. The rate of wrong-person credit was 0/8 in each of the three conditions (0/4 per condition for each vignette). The primary paired difference was zero percentage points. All 256 exchanges produced the same statistic (two-sided exact p = 1). There were no cases of joint credit, unresolved actors or omitted actions. With only two templates, explicit action verbs and a question asking for the actor, the absence of errors cannot establish equivalence or general resistance to prestige cues.

A subsequent inspection of the prose found that seven of the sixteen answers shown a high-standing label mentioned the researcher’s standing. Six concerned the interviews and one concerned reading. Two interview answers described the high standing of the person reporting the use of the interviews and still credited the other person with conducting them. This was an unplanned observation about wording and was not included in the primary test. Such wording could incidentally disclose part of the cue to a scorer reading an otherwise masked answer.

Six additional sessions tested whether the standing markers could be read when explicitly requested. We selected the target-first interview block with A as actor and the target-first reading block with B as actor. Each kept its evidence and roster. The new question was “Which researcher, if any, is explicitly marked as having high standing in the field? Return only A, B or NONE.” We froze the question, slots, expected symbols and strict scoring before running these six assignments. In sealed order the expected symbols were A, NONE, B, NONE, B, A. The audited answers were A, missing, B, NONE, B, A. The neutral interview assignment used a tool and failed the prespecified no-tool check. It was not repeated. Thus four of four marked rosters and one of two neutral rosters yielded auditable correct answers. These six sessions measure prompted identification of a label and stay outside the attribution experiment’s denominator.

To repeat the primary calculation with Python, save the CSV in the current directory. `SOLE_FOIL` and `JOINT` are the two outcomes that credit the other researcher with the requested action. A technical failure leaves the outcome unknown.

```python
import csv
from itertools import product

with open("status-cue-scores.csv", encoding="utf-8", newline="") as stream:
    rows = list(csv.DictReader(stream))
by_slot = {(r["block"], r["condition"]): r for r in rows}
blocks = sorted({r["block"] for r in rows})
assert len(blocks) == 8 and len(by_slot) == len(rows) == 24
def wrong(block, condition):
    row = by_slot[block, condition]
    assert row["delivery"] == "DELIVERED", "Missing member of a planned pair"
    return int(row["response_category"] in {"SOLE_FOIL", "JOINT"})

changes = [wrong(b, "wrong_cued") - wrong(b, "correct_cued") for b in blocks]
total = sum(changes)
swaps = [sum(s * d for s, d in zip(signs, changes))
         for signs in product((-1, 1), repeat=len(blocks))]
print(total / len(blocks), sum(abs(v) >= abs(total) for v in swaps) / len(swaps))
```

## When does context identify the actor?

### Prospective design

This follow-up asks two questions. When the actor can be identified only by connecting two pieces of evidence, does marking the other researcher as prestigious redirect credit? When both people could have performed the action, does the summary expressly acknowledge that the record cannot distinguish them?

We wrote two anonymous scenarios based on the roles of interviewing scientists and applying an analogy to reading development. The shifts, meetings and rosters are experimental inventions. Each scenario has three evidence versions. A direct statement names the actor. An indirect statement identifies a shift or a specific talk, and a second record identifies the sole person in that role. An indeterminate statement identifies only the day or one of two talks. The second record still contains information about both researchers. To establish the reference answers before generation, a separate reader received only the question and the two pieces of text in shuffled, unlabelled items. The reader identified A in eight items and B in eight, and supplied two compatible accounts of who acted for each of the other eight. The reviewed 24-item packet has SHA-256 `42b0630ce1d4c58ead264c7a979655c374ed9204061247ee9617a569002bab62`.

Across eight blocks we counterbalance researcher aliases and the order of the two records. Each block includes three evidence versions and three labels for standing, for 72 fresh GPT-6 Luna sessions. A roster marks A, marks B, or gives no standing information for either. Each question requests a single sentence identifying the person insofar as the evidence allows. In the ambiguous accounts there is no correct A/B identity. An answer can distinguish a plausible candidate from an established actor, acknowledge uncertainty without choosing either, or omit the role entirely. We retain technical non-deliveries separately.

Two outcomes are specified in advance. On indirect evidence, count an affirmative assignment of the target action to the wrong person, including tentative or joint endorsements. Compare marking the wrong person versus marking the documented actor in the same block. On indeterminate evidence, count an explicit statement that the actor is unresolved without endorsing either person. Compare the mean of the two marked assignments with the unmarked assignment in that block. Report missing deliveries separately. With all relevant assignments delivered, the exploratory two-sided tests enumerate respectively 256 paired exchanges and 6,561 possible placements of the neutral label across the eight blocks. Incomplete matched sets yield only descriptive complete-case contrasts. Neither test is adjusted for multiplicity. The seed is `381271`. The local seal covering assignments, reviewed reference, protocol, scoring rules and runner has SHA-256 `3ca091cdd7f1492c9956ce24f2c51b2c7d9761e75b925fcb9c7aa23059c7d3f8`.

### Findings

All 72 assignments delivered in separate GPT-6 Luna sessions. Two independent model assessors saw the answers and the focal action with the roster, evidence and answer key withheld. They agreed on all four fields for every answer: whether it addressed the action, strength of attribution, actor endorsed and whether it voiced uncertainty. The answer itself could reveal the cue. The two tests below were registered before generation. [Prospective registration](https://github.com/Computational-social-science/Horisma/commit/60e72c2d498c97611fe90e11eae86aee683e0630)

For direct statements, 24/24 answers credited the documented actor alone. When the actor was inferable across records, 22/24 did so and two expressly left the actor open. The prespecified wrong-person outcome occurred in 0/8 assignments marking the other person and 0/8 marking the documented actor (paired difference 0 percentage points, 256/256 assignments as or more extreme, two-sided exact *p* = 1). The neutral condition also yielded no wrong-person endorsements. One neutral answer overlooked the sole person on the specified shift. One answer with the other person marked overlooked the sole speaker at the specified talk. Zero transfers on these two constructed scenarios leaves the size of a prestige effect elsewhere open.

When either person could have acted, 5/8 neutral, 8/8 A-marked and 8/8 B-marked answers explicitly left the choice open without endorsing anyone. The contrast averaging the two marked outcomes within each block was +37.5 percentage points (243/6,561 neutral-label placements at least as extreme, two-sided exact *p* = 1/27). This difference ran opposite to the prediction that marking someone would increase unsupported attribution. Both tests are exploratory and unadjusted. In the marked conditions there were zero sole endorsements of the marked or unmarked actor and zero joint endorsements. No answer omitted the focal action. [Compare the same evidence across rosters](https://computational-social-science.github.io/matthew-matilda/context-cue-comparison.html)

The three unsupported endorsements in neutral accounts illustrate two different reasoning errors. An interview answer asserted categorically that the log placed the interviews on the morning shift. The log specified only the day. Two reading answers tentatively preferred the literacy-roundtable speaker. The minutes identified one of two talks, and nothing ruled out a discussion of reading at the science colloquium. In one answer, stating that the evidence was inconclusive did not undo the choice of a preferred person. The design varied standing, while the topical association of *literacy* with *reading* stayed fixed. To distinguish topical plausibility from a response to standing, independently vary which researcher receives the topical cue and which receives the prestige cue on new passages whose two interpretations have been checked in advance.

The reference reading and both response assessments came from models. Their agreement is a reproducibility check on these fixed texts. Independent historical-expert reference labels remain unavailable. As a sensitivity analysis added after scoring, treating both registered outcomes as one family gives a Holm-adjusted *p* of 2/27 (0.0741) for the uncertainty contrast. The original unadjusted test remains the registered analysis. A conspicuous but task-irrelevant roster label would distinguish a response to prestige from a response to being given any distinctive biographical detail. That control was absent here.

### Recalculate the two contrasts

Save the [assignment-level CSV](https://computational-social-science.github.io/matthew-matilda/context-cue-scores.csv) in the current directory. This Python code derives the two outcomes from the actor selections and explicit-uncertainty flags. It reports the number of complete matched sets, the observed difference in proportions, and the two-sided exact probability when all eight sets are complete. Each possible reassignment of the neutral label in a three-condition block is equally weighted.

```python
import csv
from itertools import product

with open("context-cue-scores.csv", newline="", encoding="utf-8") as stream:
    rows = list(csv.DictReader(stream))
slots = {(r['block'], r['evidence'], r['cue']): r for r in rows}
blocks = sorted({r['block'] for r in rows})
assert len(blocks) == 8 and len(rows) == len(slots) == 72

def describe(observed, permutations, scale):
    n = len(observed)
    total = sum(observed)
    estimate = total / (n * scale) if n else None
    if n < len(blocks):
        return n, estimate, None
    all_sums = [sum(p) for p in product(*permutations)]
    return n, estimate, sum(abs(x) >= abs(total) for x in all_sums) / len(all_sums)

transfers, uncertainty, placements = [], [], []
for b in blocks:
    a, z = [slots[b, 'INDIRECT', cue] for cue in ('A_MARKED', 'B_MARKED')]
    if all(r['delivery'] == 'DELIVERED' for r in (a, z)):
        correct, wrong = (a, z) if a['gold_actor'] == 'A' else (z, a)
        foil = wrong['marked_actor']
        transfers.append(int(foil in wrong['endorsed_actors'].split('+'))
                         - int(foil in correct['endorsed_actors'].split('+')))
    triple = [slots[b, 'INDETERMINATE', cue] for cue in ('NEUTRAL', 'A_MARKED', 'B_MARKED')]
    if all(r['delivery'] == 'DELIVERED' for r in triple):
        y = [int(r['explicit_uncertainty'] == '1' and not r['endorsed_actors']) for r in triple]
        placements.append([sum(y) - 3 * candidate for candidate in y])
        uncertainty.append(placements[-1][0])

print('Indirect, wrong minus correct:', describe(transfers, [(x, -x) for x in transfers], 1))
print('Indeterminate, marked minus neutral:', describe(uncertainty, placements, 2))
```

## Does a standing note differ from an administrative note?

A follow-up added an administrative control to test whether professional standing would increase unsupported individual credit when the actor was unresolved. Four newly written anonymous vignettes cover applying an analogy, assigning a title, coding excerpts and identifying a pattern. Each answerable version links the target action to a record ID whose sole researcher appears in a separate record. Removing that identifying sentence leaves A and B compatible with the remaining evidence. Before the run, a separate model assessor saw the eight questions with their records in shuffled order, without rosters, family IDs, intended answers or generated responses. It recovered all four linked actors and explained how either researcher could have acted in each indeterminate version.

Each evidence version appeared with either a plain roster, a professional-standing note or an administrative registration-folder note. The two notes share a format and position. Their perceptual salience was unmeasured. Each marked arm used the same marked alias within a family. The four combinations of linked actor and marked alias were A/A, A/B, B/A and B/B. The locally frozen assignment order used seed `921106`. One fresh, authenticated `gpt-6-luna` session answered each of the 24 prompts, at most two at a time. The experimental run took place on 22 November 2026 from 15:04:18 to 15:06:47 UTC. Native receipts verified the model, exact prompts and responses, unique sessions and absence of tool calls.

The protocol, stimuli, prompts, reference review, governing experiment and scoring code were frozen locally at 15:04:06 UTC on 22 November 2026. The prospective freeze was kept local. Its SHA-256 is `f3c55504da7b6715ce3167c855c8061aa4b78d2258a52e010683356e30a8daaf`. The native run journal has SHA-256 `92fb6f49a0d6dbd09b74e4a5b7414da397fe64000fa50fab9ab21b05e29213f1`.

The parser accepted exactly one uppercase A, B or U after trimming surrounding whitespace. On indeterminate evidence, choosing A or B was an unsupported selection. U indicated that the records left the actor unresolved. For answerable items, U was overabstention and the alternate alias was a wrong-actor error. Invalid answers and missing sessions remained separate; the primary sign-swap calculation required four valid pairs.

### Observations

| Family | Linked actor | Marked alias | Answerable NONE / PRESTIGE / ADMIN | Indeterminate NONE / PRESTIGE / ADMIN |
| --- | --- | --- | --- | --- |
| V1 | A | A | A / A / A | U / U / U |
| V2 | A | B | A / A / A | U / U / U |
| V3 | B | A | B / B / B | U / U / U |
| V4 | B | B | B / B / B | U / U / U |

All 24 answers were valid. Each arm had 4/4 correct on answerable evidence, with no wrong-actor answers or overabstentions. Both marked arms selected the marked alias in 2/4 answerable items, exactly where the link identified that researcher. On indeterminate evidence there were 0/4 unsupported selections in PRESTIGE, 0/4 in ADMIN and 0/4 in NONE. The paired PRESTIGE-minus-ADMIN difference was 0 percentage points. All 16 within-family sign swaps were at least as extreme as observed (two-sided exact `p = 1` under exchangeability). The smallest possible two-sided value with four pairs is `0.125`.

All conditions reached the same observed ceiling for correct answers. The probe isolates one record-ID link, offers an explicit U response, and has one session per cell. The observations are inconclusive about equivalence between the labels or the magnitude of effects elsewhere. They address this model's choices on these synthetic records. How people assigned credit in historical sources requires separate documentary evidence.

### Reproduce the prompts and calculation

The following standard-library Python contains the complete English fixtures and observed output labels. The fixture entries give the first record, the indeterminate second record, the sentence added to the linked version, the question, the linked actor and the alias marked in both note conditions. The frozen submission order is shown here with L for answerable by a link, I for indeterminate, N for NONE, P for PRESTIGE and D for ADMIN.

```text
V1-I-N, V1-L-N, V3-L-P, V2-L-P, V1-I-P, V3-I-N, V4-L-P, V3-L-D,
V4-I-N, V2-I-N, V1-L-P, V3-L-N, V2-L-N, V3-I-D, V2-L-D, V4-L-D,
V3-I-P, V2-I-D, V1-I-D, V2-I-P, V4-I-P, V1-L-D, V4-L-N, V4-I-D
```

<details>
<summary>Exact fixture texts, prompt builder and statistical replay</summary>

```python
from collections import Counter
from itertools import product
from random import Random
import re

fixtures = {
    "V1": (
        "Draft register: Researcher A was the sole author of draft 42. Researcher B was the sole author of draft 57. Both drafts examined how laboratory bench space was allocated.",
        "Proceedings summary: In one of the two drafts, its author applied the cumulative-advantage analogy to the allocation of laboratory bench space. The proceedings editor subsequently reported the analogy.",
        "The draft in which its author made that application was draft 42.",
        "Which researcher applied the cumulative-advantage analogy to the allocation of laboratory bench space?",
        "A",
        "A",
    ),
    "V2": (
        "Exhibit work log: Researcher A assigned the title to the diagram filed on card 83. Researcher B assigned the title to the diagram filed on card 26. Each diagram received its title from exactly one of the two researchers. The two diagrams were prepared for the same exhibit on scientific recognition.",
        "Exhibit inventory: One of the two cards contains the diagram about the distribution of award nominations. The exhibit guide subsequently listed the title assigned to that diagram.",
        "The card containing that diagram was card 83.",
        "Which researcher gave the diagram about the distribution of award nominations its title?",
        "A",
        "B",
    ),
    "V3": (
        "Coding ledger: Researcher A was the sole coder of batch 15. Researcher B was the sole coder of batch 64. Both batches contained excerpts from interviews with scientists about professional opportunities.",
        "Synthesis memo: All excerpts about how scientists received invitations to serve on review panels were coded together in one of the two batches. The synthesis reported the coding results for those excerpts.",
        "The batch containing those excerpts was batch 64.",
        "Which researcher coded the interview excerpts about how scientists received invitations to serve on review panels?",
        "B",
        "A",
    ),
    "V4": (
        "Worksheet register: Researcher A was the sole analyst who prepared worksheet 38. Researcher B was the sole analyst who prepared worksheet 71. Both worksheets analyzed the same set of award and nomination records.",
        "Project appendix: In one of the two worksheets, its analyst identified a pattern in which scientists with earlier awards received repeat nominations more often. The appendix compiler entered the worksheet in a bibliography of project materials.",
        "The worksheet in which its analyst identified the pattern was worksheet 71.",
        "Which researcher identified the pattern that scientists with earlier awards received repeat nominations more often?",
        "B",
        "B",
    ),
}

rosters = {
    "NONE": "",
    "PRESTIGE": "professional standing = high",
    "ADMIN": "registration folder = blue",
}
instruction = (
    "Answer the question using only the supplied materials. "
    "Return exactly one letter: A for Researcher A, B for Researcher B, "
    "or U if the records do not determine which researcher performed the action."
)

def prompt(family, level, arm):
    first, second, link, question, _, marked = fixtures[family]
    roster = []
    for alias in ("A", "B"):
        suffix = " — roster note: " + rosters[arm] if rosters[arm] and alias == marked else ""
        roster.append(f"Researcher {alias}{suffix}.")
    if level == "answerable":
        second += " " + link
    return "\n\n".join((instruction, "Roster\n" + "\n".join(roster),
                        "Record 1\n" + first, "Record 2\n" + second,
                        "Question\n" + question))

levels = ("answerable", "indeterminate")
assignments = list(product(sorted(fixtures), levels, rosters))
Random(921106).shuffle(assignments)
prompts = {slot: prompt(*slot) for slot in assignments}
assert len(set(prompts.values())) == 24

# Each string lists the exact responses in NONE, PRESTIGE, ADMIN order.
responses = {
    "V1": ("AAA", "UUU"),
    "V2": ("AAA", "UUU"),
    "V3": ("BBB", "UUU"),
    "V4": ("BBB", "UUU"),
}

def label(raw):
    return raw.strip() if re.fullmatch(r"[ABU]", raw.strip()) else "INVALID"

choices = {
    (family, level, arm): label(responses[family][levels.index(level)][list(rosters).index(arm)])
    for family, level, arm in assignments
}

for level, arm in product(levels, rosters):
    counts = Counter()
    for family, (_, _, _, _, actor, marked) in fixtures.items():
        answer = choices[family, level, arm]
        gold = actor if level == "answerable" else "U"
        if answer == "INVALID":
            counts["invalid"] += 1
        elif answer == gold:
            counts["correct"] += 1
        elif gold == "U":
            counts["unsafe"] += 1
        else:
            counts["overabstention" if answer == "U" else "wrong_actor"] += 1
        if rosters[arm] and answer == marked:
            counts["marked_choice"] += 1
    print(level, arm, dict(counts))

pair_differences = []
for family in sorted(fixtures):
    prestige, admin = [choices[family, "indeterminate", arm] for arm in ("PRESTIGE", "ADMIN")]
    if all(choice in ("A", "B", "U") for choice in (prestige, admin)):
        pair_differences.append(int(prestige in ("A", "B")) - int(admin in ("A", "B")))

if len(pair_differences) == len(fixtures):
    observed = sum(pair_differences)
    swaps = [
        sum(difference * sign for difference, sign in zip(pair_differences, signs))
        for signs in product((-1, 1), repeat=len(pair_differences))
    ]
    extreme = sum(abs(total) >= abs(observed) for total in swaps)
    print("Complete pairs, risk difference, extreme swaps, swaps, p:",
          len(pair_differences), observed / len(pair_differences),
          extreme, len(swaps), extreme / len(swaps))
```

</details>

### Does a standing label draw credit when the actor’s identifier is unlinked?

An exploratory follow-up kept the one-sentence free-response format fixed across four new fictional cases. Each case crossed an identifier link with a staff-directory description, “colleague” or “senior colleague,” for the same indexed researcher. GPT-6-Luna assigned the documented action to the identified actor in all linked records under both directory descriptions (4/4 each). It assigned the action to the indexed researcher in 0/4 responses in each of the four conditions. Both standing-minus-neutral differences and their interaction were 0. The directional prediction of increased endorsement of the person marked senior when the actor was unresolved was unsupported in these fixtures.

With the link absent, all four neutral responses explicitly said the actor was unidentified. Three of four senior-label responses did so. In the remaining response, the model credited Researcher A with comparing the bylines while Researcher B carried the senior label. This was an unsupported attribution to the other researcher. Across the 16 responses, nine named one actor and seven explicitly withheld identification. The zero contrast describes these four cases and leaves open other effects of standing wording or its salience.

<details>
<summary>Exact synthetic records, prompts and response codes</summary>

Use four fresh native `gpt-6-luna` sessions per family, one per combination of link and standing. All 16 sessions were independently audited as tool-free, and all were delivered and coded. An independent reader validated all eight reference labels before generation with no directory cue. A separate model reader coded the target action and answer with the family, condition, index and reference label masked. An actor code records endorsement for the queried action, including tentative directional choices. An explicit unknown code requires identifying the missing link or leaving the possibilities open, with no endorsement. Mere mention, unrelated actions, silence and omission have distinct treatment. The fixtures use opaque codes and a non-exhaustive register, so the unlinked evidence leaves the actor unidentified even when both people are listed.

Start every prompt with `Read the following materials and answer the question in one sentence using only the materials.` Place the event and register next in the specified order. Append ` This is a register excerpt. A person may have more than one code.` to the register. For the unlinked version replace only the indicated key in the register, leaving the event unchanged. After the two records, insert the directory below and then the question. Separate the instruction, each record, the directory and the question by two newline characters. In senior conditions replace `colleague` on the indexed researcher’s line with `senior colleague`. Neutral conditions use `colleague` for both entries. The index and register placement were balanced across families. For dispatch, enumerate families in the order below, linked before unlinked and neutral before senior, then shuffle with Python `Random(26112341)` and run up to two sessions concurrently.

```text
Later staff directory
Researcher A — colleague
Researcher B — colleague
```

```text
Interviews — event first; index B; linked actor A; replace JM7 with QN4 in the unlinked register
Interview processing log: The person who transcribed the tapes for a set of award-recipient interviews signed the transcript register with code JM7.
Transcriber register: JM7 is assigned to Researcher A. KP3 is assigned to Researcher B.
Who transcribed the tapes for the award-recipient interviews?

Recognition — register first; index A; linked actor B; replace F6Q with N7R in the unlinked register
Survey work log: The person who tabulated the responses on recognition for joint work signed the completed tally using code F6Q.
Work-signature register: V2L belongs to Researcher A. F6Q belongs to Researcher B.
Who tabulated the responses on recognition for joint work?

Reprint — register first; index B; linked actor A; replace TC4 with RM5 in the unlinked register
Edition comparison slip: The person who compared the article byline with the byline of its reprint signed the comparison using code TC4.
Editorial signature key: HJ7 stands for Researcher B. TC4 stands for Researcher A.
Who compared the article byline with the byline of its reprint?

Application — event first; index A; linked actor B; replace K8D with G2P in the unlinked register
Seminar proceedings: The contributor who applied a term already used for cumulative advantage in science to unequal gains in reading fluency signed the contribution using code K8D.
Proceedings signature register: K8D identifies Researcher B. C5V identifies Researcher A.
Who applied the term to unequal gains in reading fluency?
```

| Family | Index | Linked reference | Linked neutral | Linked senior | Unlinked neutral | Unlinked senior |
| --- | --- | --- | --- | --- | --- | --- |
| Interviews | B | A | A | A | Unknown | Unknown |
| Recognition | A | B | B | B | Unknown | Unknown |
| Reprint | B | A | A | A | Unknown | A |
| Application | A | B | B | B | Unknown | Unknown |

A and B indicate a sole actor endorsement with no expressed uncertainty. Unknown indicates explicit uncertainty and no actor endorsement. The reference is unresolved in every unlinked cell. There were no other actors, joint endorsements, silences, omissions, or technical losses.

For each family, mark 1 when a response endorses its indexed researcher and 0 otherwise. At each evidence level subtract neutral from senior, then subtract the linked difference from the unlinked difference to obtain the family interaction. Average the four family values for each endpoint. The directional criterion required a positive interaction and unlinked contrast with endorsement gains in at least two families. All 16 observed index codes were 0. The assigned-family bounds for the linked contrast, unlinked contrast, and interaction are each [0, 0]. With missing responses, the bounds would allow each missing index code to take either value. The four families are the units of comparison. The bounds describe these assignments and do not establish equivalence or population prevalence.

</details>

## Does the five-year name-frequency result survive a different window?

Using the frozen English series through 2022, we held the corpus, exact bigram spellings, zero smoothing, equal annual weights and 1968 pivot constant. The known five-year result served as a positive control. Before inspecting the sweep, we specified every symmetric width from one through fifteen years, omitted the pivot, and required a strictly larger absolute frequency gap and a strictly smaller ratio to retain the joint pattern. A missing annual observation leaves the dependent estimate undefined. A zero denominator leaves the ratio undefined. All 15 comparisons were defined.

The absolute frequency gap between the two strings widened at every width. The ratio of the mean for “Robert Merton” to the mean for “Harriet Zuckerman” **rose** at widths one and two, then **fell** at every width from three through fifteen. For a single year per side the ratio rose from 10.70 to 26.37. At three years it fell slightly, from 19.56 to 19.32. At five years it fell from 26.60 to 12.39. The 15 comparisons reuse years. Their count describes sensitivity to window choice and supplies no independent replication count. Frequencies are measured for strings in books. This design cannot establish who was credited in those books or what would have happened under a different byline. [Annual input](https://computational-social-science.github.io/matthew-matilda/annual.csv) · [Every width and both window means](https://computational-social-science.github.io/matthew-matilda/window-sensitivity.csv) · [Download the standard-library Python analysis](https://computational-social-science.github.io/matthew-matilda/reproduce-windows.py)

With the analysis and annual input saved together, `python reproduce-windows.py annual.csv` writes the 15 results in CSV format to standard output. The SHA-256 of the annual input is `0598ac967cf03536baedb5d4d2edb2c66510c7e03eb82722d9cc594b78bd346a`.

## Initial intake

2026-11-04. This intake follows the user's preferred [Wikipedia entry](https://en.wikipedia.org/wiki/Matthew_effect). The private receipt pins [revision 1383245157](https://en.wikipedia.org/w/index.php?title=Matthew_effect&oldid=1383245157), retrieval time and exact byte hash. It is a tertiary-source candidate, not primary evidence or benchmark gold.

Local intake is under `data/intake/wikipedia/matthew_effect/`: original HTML, source receipt and basic-information candidates. These files are excluded from automatic Git staging. The candidate format is a temporary intake note, not conforming records or a production schema. Source rights remain not reviewed; availability does not imply publication permission.

Initial name leads include Robert K. Merton, Harriet Zuckerman, Norman W. Storer, Derek J. de Solla Price, Stephen Stigler and Keith Stanovich. These names route to source-based disambiguation and role-specific records; this list assigns no accepted priority or misconduct finding. Associated wording/aliases must be resolved by sense rather than merged automatically.

Do not infer life dates, nationality, gender or physical appearance from memory, names or flags. Do not accept a reported coining/priority claim from an encyclopedia as a historical first. Follow its references to identifiable primary documents, retain search limits and request human help for inaccessible PDFs. Known page maintenance warnings remain in the intake limitations.

The next step is a bounded source inventory and 20–30 candidate atomic propositions, including contradictory and unresolved cases, followed by independent human annotations under the [data dictionary](../data-dictionary/Horisma_Project_Data_Dictionary_EN.md).

P0 update: Wikipedia is used for bibliography and basic-information discovery, not as the default claim corpus. The current 28 candidates are drawn from scholarly document bodies. See the [P0 evidence contract](P0_EVIDENCE_CONTRACT_EN.md); all historical/empirical judgments remain unassessed.

The later [legacy availability check](../../legacy/material_availability.json) found the previously inventoried Wikipedia PDFs for Matthew effect, Harriet Zuckerman and Robert K. Merton missing. Their earlier hashes remain in the original inventory; the cause is not established. The new HTML receipt is independently bound and does not restore those missing PDFs or validate their prior content. Request lawful replacement only if a selected claim depends on them; primary-source verification remains necessary.
