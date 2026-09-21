# Everything unresolved, with context

Complete list from run 4, the `\&` + B4 + colon-locator + `cp.` implementation.
Nine in-profile reconciling papers. 29 August 2026.

Four different things get called "missing", so all four are here:

```text
  109  unresolved citations   text we saw and could not parse
   59  unresolved references  bibliography lines we could not parse
   36  missing_reference      citation parsed, no matching entry
   33  uncited_reference      entry parsed, nothing cites it
    5  ambiguous_citation     one key, several entries
    5  possible_mismatch      near-miss pairing
    5  duplicate_reference_key
```

Verdicts are mine and are the classification, not a decision. SPECIFIED means
already agreed and unimplemented. NEW GRAMMAR needs an rc3 call. LIMITATION is
a register candidate. NOT A CITATION means the detector proposed it and the
grammar was right to refuse.

---

## Read this first — 10 of the 36 `missing_reference` records are our defect

Before reading the list as a list of paper defects: some of it is ours.

**Possessive genitive — 7 records, 13 occurrences.**

```text
Tepper's (2000)      -> tepper's|2000       reference is  tepper|2000
Hambrick's (2007)    -> hambrick's|2007
Leventhal's (1980)   -> leventhal's|1980
Colquitt's (2001)  ·  Fine's (1998)  ·  Bartko's (1976)  ·  Fotiadis's (2018)
```

The `'s` goes into the key, so the citation can never pair. This is R1, already
known from the first run, and it is exactly what B7 possessive normalisation
fixes: strip the suffix for the normalised identity only, leave the raw span
alone.

**Hyphen loss in conversion — 3 records.**

```text
KabatZinn, 2003             -> kabatzinn|2003         Kabat-Zinn
KabatZinn, 1982             -> kabatzinn|1982
DonaldsonFeilder, …, 2018   -> donaldsonfeilder|2018  Donaldson-Feilder
```

All three in one paper. Mathpix dropped the hyphen, so this belongs with `\&`
in the conversion-artefact layer, not in the grammar.

**And it compounds, in three confirmed cases.**

```text
fine's|1998       missing_reference     AND   fine|1998       uncited_reference
bartko's|1976     missing_reference     AND   bartko|1976     uncited_reference
colquitt's|2001   missing_reference     AND   colquitt|2001   uncited_reference
```

One defect, two false diagnostics, on opposite sides of the reconciliation. The
other seven do not pair only because those references happen to be cited
correctly somewhere else in the same paper.

So `missing_reference` at 36 is an upper bound on paper defects. At least 10 are
ours, and fixing them also removes three false `uncited_reference` records.

---

## 1. Unresolved citations (109)

### B5  lead-in cue — 17

**SPECIFIED — B5 bounded lead-in**

- `for an overview: Schyns and Schilling, 2013`
  - 43338825 · INTRODUCTION · byte 8409
  - context: For example, follower stress is related to the perception of abusive supervision (e.g., Tepper, 2000; Chen and Kao, 2009; for an overview: Schyns and Schilling, 2013).
- `(see for example Martinko et al., 2012)`
  - 43338825 · INTRODUCTION · byte 9200
  - context: Therefore, to better understand the effects of abusive leadership and the validity of the perception of abusive supervision, it is necessary to investigate abusive supervision in a way which allows us to systematically control actual leadership behavior so that differences in follower perception of and reactions to identical behavior can be attributed to follower characteristics with confidence (s …
- `Martinko et al. (2013, see also Brees et al., 2016)`
  - 43338825 · INTRODUCTION · byte 10637
  - context: In their comprehensive overview, Martinko et al. (2013, see also Brees et al., 2016) convincingly argue that it is important to distinguish between perceived and actual abusive supervision as we cannot be sure if perceived leader abuse is a valid proxy for actual behavior.
- `(see Martinko et al., 2013, for a critique)`
  - 43338825 · ABUSIVE LEADERSHIP AND FOLLOWER REACTIONS · byte 13257
  - context: Very often findings of relationships between follower ratings of abusive supervision and outcomes are interpreted as if those follower ratings are a direct and perfect assessment of actual leader behavior (see Martinko et al., 2013, for a critique).
- `(for an overview see Hansbrough et al., 2015)`
  - 43338825 · ABUSIVE LEADERSHIP AND FOLLOWER REACTIONS · byte 13429
  - context: However, follower ratings are influenced by rater characteristics such as personality, implicit leadership theories, or affect (for an overview see Hansbrough et al., 2015).
- `(see Harvey et al., 2014, for a recent meta-analysis)`
  - 43338825 · ATTRIBUTION OF ABUSIVE SUPERVISOR BEHAVIOR AS A MODERATOR IN THE RELATIONSHIP BETWEEN PERCEPTIONS OF ABUSIVE SUPERVISION AND FOLLOWER REACTIONS · byte 20385
  - context: Attributions have been shown to be important factors in predicting workplace outcomes and reactions (see Harvey et al., 2014, for a recent meta-analysis).
- `(see Martinko et al., 2013, for an overview)`
  - 43338825 · Overview · byte 58452
  - context: At the same time, we expect that actual leader behavior is more ambiguous and that, consequently, we will find a stronger effect of the control variables (follower characteristics; specifically, negative affectivity, hostile attribution style, trait anxiety, and irritation) on the perception of abusive supervision in the field study, comparable to previous studies (see Martinko et al., 2013, for a …
- `(for a recent review, see Good et al., 2016)`
  - 4918fd7d · Abstract · byte 8720
  - context: Secondly, it contributes to the literature on mindfulness in the work context (for a recent review, see Good et al., 2016).
- `(for an overview, see, e.g., Iszatt-White & Kempster, 2018)`
  - 4918fd7d · Authentic Leadership · byte 10643
  - context: The psychological leadership literature has borne many definitions and discussions of authenticity and authentic leadership in the past years (for an overview, see, e.g., Iszatt-White & Kempster, 2018).
- `see e.g., Hafenbrack, Kinias, & Barsade, 2014`
  - 4918fd7d · Results Study 2 · byte 58961
  - context: Manipulation Check Following the recommendation from Donaldson-Feilder et al. (2018) and a number of prior mindfulness intervention studies (see e.g., Hafenbrack, Kinias, & Barsade, 2014; Hülsheger et al., 2015; Michel et al., 2014), we tested whether the mindfulness intervention was actually effective (i.e., led to an increase in mindfulness).
- `for critiques, see e.g., Davidson & Kaszniak, 2015`
  - 4918fd7d · Limitations and Future Directions · byte 73964
  - context: By implementing random group assignment in combination with pre- and postintervention measurements, our study responded to recent calls for more rigorous designs in mindfulness intervention studies (for critiques, see e.g., Davidson & Kaszniak, 2015; Donaldson-Feilder et al., 2018; Eby et al., 2017; Jamieson & Tuckey, 2017; Lomas et al., 2017).
- `(see e.g., Purser & Loy, 2013)`
  - 4918fd7d · A Final Note · byte 81223
  - context: Two points are important to note in that regard: First, it has been discussed whether mindfulness meditation will always lead to more acceptance and kindness, uncovering people's natural well of goodness, or if it may also be misused for doing harm with greater attentiveness and precision (see e.g., Purser & Loy, 2013).
- `for a similar approach, see Osadchiy et al., 2015`
  - ad1e3ff9 · Data collection and cleaning process · byte 31393
  - context: [^0]collection, allowing us to capture supply chain structure in 2015 (for a similar approach, see Osadchiy et al., 2015; Kim and Davis, 2016; Sharma et al., 2019a).
- `(see Bloomberg 2011, 2013 for details)`
  - ad1e3ff9 · Data collection and cleaning process · byte 36399
  - context: For each sampled focal firm, we collected customer/supplier lists and other tie-level data, including a percentage of the supplier's revenue from each customer, a percentage of the customer's spend on each supplier, and whether a tie involved the supply of goods (COGS), capital expenditures, research and development, or administrative services (see Bloomberg 2011, 2013 for details).
- `(for a meta-analysis, see Colquitt et al., 2013)`
  - e1b418a4 · Abstract · byte 3524
  - context: On the other hand, research has shown that people are better off when their overall level of fair treatment is higher as opposed to lower (for a meta-analysis, see Colquitt et al., 2013).
- `(for a review, see Sonnentag & Frese, 2003)`
  - e1b418a4 · Justice Variability and Stress · byte 16917
  - context: Indeed, the notion that a lack of control is stressful is featured prominently not only in uncertainty management theory, but also in other models of stress (for a review, see Sonnentag & Frese, 2003).
- `for comparative examples, see Koopman, Lanaj, & Scott, 2016`
  - e1b418a4 · Analysis · byte 63110
  - context: Specifically, we used the Bauer, Preacher, and Gil (2006) formula to capture the magnitude of the indirect effects and used a Monte Carlo simulation with 20,000 replications to construct confidence intervals around the estimated indirect effects (for comparative examples, see Koopman, Lanaj, & Scott, 2016; Lanaj, Johnson, & Barnes, 2014; Wang, Liu, Liao, Gong, Kammeyer-Mueller, & Shi, 2013).

### bare year — 16

**NOT A CITATION — detection artefact**

- `(2013)`
  - 43338825 · FOLLOWER CHARACTERISTICS AS CONTROL VARIABLES · byte 23538
  - context: Based on Martinko et al.'s review (2013) as well as previous research on followers' personality on the perception and acceptance of transformational leadership (Felfe and Schyns, 2010), we argue that follower characteristics influence the perception of abusive supervision.
- `(2017)`
  - 43338825 · FOLLOWER CHARACTERISTICS AS CONTROL VARIABLES · byte 23996
  - context: In Mackey et al.'s (2017) meta-analysis, negative affectivity was the strongest antecedent of the perception of abusive supervision and therefore we included negative affectivity in our study in order to control for this potential bias.
- `2016`
  - 43338825 · FOLLOWER CHARACTERISTICS AS CONTROL VARIABLES · byte 24228
  - context: Brees et al. (2016; see also Martinko et al., 2013) highlight the role of hostile attribution style, which we also take forward as a follower characteristic.
- `(2002)`
  - 4918fd7d · Authentic Leadership · byte 11327
  - context: Drawing on Harter's definition of authenticity (2002), the model emphasizes the congruence of one's thoughts, feelings, preferences, and beliefs with one's actions.
- `(2012,2016)`
  - 4918fd7d · Leaders' Trait Mindfulness and Authentic Leadership · byte 19437
  - context: Additional work by Baron $(2012,2016)$, which focused on the effects of extensive leader action learning programs, showed that leaders' trait mindfulness was crosssectionally related to their ratings of their authentic leadership behavior.
- `(2012,2016)`
  - 4918fd7d · The Effect of a Mindfulness Intervention and Authentic Leadership · byte 38239
  - context: The study by Baron $(2012,2016)$ tested an extensive 3-year action learning program with a multitude of elements (of which mindfulness was one small part), while the pilot study by Wasylkiw et al. (2015) investigated the effect of a meditation weekend retreat.
- `(2012,2014)`
  - 50408397 · System Justification Theory and the Belief in the Business Case for CSR · byte 27081
  - context: For instance, Shepherd and Kay $(2012,2014)$ provided evidence that individuals who score higher on system justification try harder to avoid information about economic issues during a recession or about companies involved in environmental scandals.
- `(2003a)`
  - 50408397 · Measures · byte 54012
  - context: As in Study 1, participants completed the systemic fair market ideology scale developed and tested by Jost and colleagues (2003a) (Cronbach's $\alpha$ in this sample = 0.70, $M=$ $-0.21, S E M=0.11)$.
- `(2015)`
  - 50408397 · Measures · byte 61224
  - context: We instructed participants to imagine that they were the CEO of a large company and then asked them to what extent they would ensure that their company engaged in the actions and policies described in the items of El Akremi et al.'s (2015) scale.
- `(2003a)`
  - 50408397 · Measures · byte 63316
  - context: As in studies 1, 2, and 3, participants completed the systemic fair market ideology scale developed and tested by Jost and colleagues (2003a) (Cronbach's $\alpha$ in this sample = $0.70, M=0.21, S E M=0.12)$.
- `(2011, 2012, and 2013)`
  - 849f8fc6 · Introduction · byte 11031
  - context: Since 1980, Spanish GDP has grown continuously with seven year-onyear declines, three consecutive (2011, 2012, and 2013) and a sharp decline because of COVID-19 (Expansion, 2022).
- `(2022)`
  - c1d56945 · Practices · byte 26332
  - context: For instance, Fremout et al (2022) discuss the advantages of combining local varieties with genotypes from areas with similar climates to the predicted future climate of the target locality.
- `(2012)`
  - e1b418a4 · Measures · byte 56650
  - context: We measured general workplace uncertainty using the four-item scale developed by Colquitt and colleagues (2012).
- `(2009)`
  - e1b418a4 · Measures · byte 58654
  - context: We measured CWB using the six-item Dalal and colleagues (2009) CWB toward the supervisor scale.
- `(2014)`
  - e1b418a4 · GENERAL DISCUSSION · byte 82441
  - context: Scott et al.'s (2014) results suggest that interpersonal justice rules exhibit the most withinperson variation, followed by informational, procedural, and distributive justice rules respectively (likely due to the varying level of discretion that supervisors have over these rules).
- `(2014)`
  - e1b418a4 · GENERAL DISCUSSION · byte 82895
  - context: If additional studies replicate Scott et al.'s (2014) results, then the key to predicting justice variability may lie in first predicting variability in respectfulness and propriety, followed by predicting variability in justifications and truthfulness, and so on.

### prose fragment — 11

**NOT A CITATION — detection artefact**

- `external and unstable attributions: e.g., leader stress, time or task pressure`
  - 43338825 · GENERAL DISCUSSION · byte 86035
  - context: For example, we would assume that the effects of abusive supervision on reactions might be mitigated by attributions toward circumstances (external and unstable attributions: e.g., leader stress, time or task pressure; cp.
- `e.g., goal setting or intellectual stimulation`
  - 4918fd7d · Abstract · byte 4343
  - context: Traditional leadership trainings focusing merely on a specific set of skills (e.g., goal setting or intellectual stimulation; Barling, Weber, & Kelloway, 1996; Dvir, Eden, Avolio, & Shamir, 2002) will fall short in this case.
- `e.g., using images and metaphors in a speech`
  - 4918fd7d · Abstract · byte 4573
  - context: In addition, training leaders to behave in a standardized, presumably ideal, way (e.g., using images and metaphors in a speech; Antonakis, Fenley, & Liechti, 2011; Emrich, Brower, Feldman, & Garland, 2001; Naidoo & Lord, 2008) without considering if this behavior is congruent or incongruent with a person's character or values, may increase the chance that both, leaders themselves and followers, pe …
- `cognitive decentering`
  - 4918fd7d · Leaders' Trait Mindfulness and Authentic Leadership · byte 23211
  - context: Moreover, mindfulness can promote leaders' selfregulation by inclining them to mentally step back (cognitive decentering; Bishop et al., 2004), which helps them to regulate and express their emotions appropriately and effectively.
- `psychological capital, leader self-knowledge and self-consistency`
  - 4918fd7d · General Discussion · byte 70829
  - context: Thus, in contrast to previous studies that focused on more stable dispositional characteristics as antecedents of authentic leadership (psychological capital, leader self-knowledge and self-consistency; Jensen & Luthans, 2006; Peus, Wesche, Streicher, Braun, & Frey, 2012), our study provides hope for the many people who are not natural-born leaders and could use support in developing their individ …
- `e.g., from the Minnesota Satisfaction Questionnaire`
  - 4918fd7d · Limitations and Future Directions · byte 76732
  - context: For example, previous research did find a relation between authentic leadership and followers' job satisfaction (e.g., Neider & Schriesheim, 2011)-at least when using job satisfaction measures that contain items directly referring to supervision (e.g., from the Minnesota Satisfaction Questionnaire; Weiss, Dawis, Lofquist, & England, 1967).
- `e.g., emotional stability, conscientiousness, psychological capital, leader self-knowledge and self-consistency`
  - 4918fd7d · Limitations and Future Directions · byte 78447
  - context: Thus, future studies may test the potential moderating influence of factors that have already been linked to mindfulness or authentic leadership (e.g., emotional stability, conscientiousness, psychological capital, leader self-knowledge and self-consistency; Giluk, 2009; Jensen & Luthans, 2006; Peus et al., 2012).
- `what organizational scholars would call interpersonal justice or fairness`
  - e1b418a4 · Abstract · byte 2854
  - context: One day, he treats you with dignity and respect (what organizational scholars would call interpersonal justice or fairness; Bies & Moag, 1986; Greenberg, 1993), and, the next day, he doesn't.
- `i.e., distributive, procedural, informational, and interpersonal`
  - e1b418a4 · DEFINING JUSTICE VARIABILITY · byte 11910
  - context: Second, although our focus is on variability in the overall level of fair treatment, that focus is not meant to deny the potential existence (and importance) of variability in the specific dimensions of justice typically examined in the literature (i.e., distributive, procedural, informational, and interpersonal; e.g., Colquitt, 2001).
- `i.e., respect and dignity`
  - e1b418a4 · Manipulations · byte 26323
  - context: Considering that our context focused on repeated electronic statements made by supervisors over a short period of time, we felt it would be most appropriate to manipulate interpersonal rules of justice (i.e., respect and dignity; Greenberg, 1993).
- `as past research on average justice has shown`
  - e1b418a4 · GENERAL DISCUSSION · byte 81719
  - context: Indeed, justice variability seems to add to the uncertainty management problem, not buffer it (as past research on average justice has shown; Van den Bos, 2001; Van den Bos & Miedema, 2000).

### multi-token surname — 9

**NEW GRAMMAR — multi-token surname**

- `Pircher Verdorfer, 2016`
  - 4918fd7d · Abstract · byte 9103
  - context: While there is an incipient body of research on the benefits of mindfulness for leadership behavior, extant studies have predominantly investigated the role of leaders' trait mindfulness for other leadership approaches, such as transformational and abusive supervision or servant leadership (Liang et al., 2016; Pinck & Sonnentag, 2017; Pircher Verdorfer, 2016).
- `(Pircher Verdorfer, 2016)`
  - 4918fd7d · Mindfulness · byte 13360
  - context: Mindfulness is an inherent human capacity that can be experienced by everyone, but it may vary in strength across situations and individuals (Pircher Verdorfer, 2016).
- `El Akremi et al. (2015)`
  - 50408397 · Measures · byte 61329
  - context: Specifically, we selected the three items with the highest factor loadings, as reported by El Akremi et al. (2015), for the domains of communityoriented CSR, natural environment-oriented CSR, employee-oriented CSR, and supplier-oriented CSR, and averaged these 12 items into a CSR engagement score (Cronbach's $\alpha$ in this sample $=0.85, M=2.95$, $S E M=0.11)$.
- `Carrieri de Souza et al., 2023`
  - c1d56945 · Stakeholders' collective actions · byte 27659
  - context: The collaborations identified have a high range of topics, some of them are the following: local food systems and market linkages for agroecological farmers (Carrieri de Souza et al., 2023; Levidow et al., 2023); networks to support and consolidate production among agroecological farmers (Resque et al., 2019; Wardell et al., 2021); facilitation of agroecological transitions (Miller et al., 2022; W …
- `Carrieri Souza`
  - c1d56945 · Stakeholders' collective actions · byte 30281
  - context: Certain stakeholders play a pivotal function in the transition toward agroecological farming, this type of stakeholders provide an enabling organizational structure for consolidating production, providing assisting services, balancing supply and demand, like farmers' cooperatives do (Bisht et al., 2020; Carrieri Souza; Moraine et al., 2016).
- `Carrieri de Souza et al. (2023)`
  - c1d56945 · Market linkages · byte 32161
  - context: Carrieri de Souza et al. (2023) highlight how these chains promote agrobiodiversity and encourage sustainable practices such as composting, waste reduction, and resource efficiency.
- `Additionally, Oliviera da Silva et al. (2023)`
  - c1d56945 · Market linkages · byte 35135
  - context: Additionally, Oliviera da Silva et al. (2023) observe that global market trends drive agricultural intensification, often at the expense of native vegetation and biodiversity.
- `Carrieri de Souza et al., 2023`
  - c1d56945 · Thematic synthesis · byte 54153
  - context: Yet, the economic effect of these practices is favorable in contexts where farmers directly sell the crops to consumers, when they have property rights on the land, when they participate in projects supported by international NGOs or are associated in enabling organizations such as farmers' cooperative (Carrieri de Souza et al., 2023; Resque et al., 2019; Wardell et al., 2021; Wezel et al., 2016). …
- `(Oliveira da Silva et al., 2024)`
  - c1d56945 · Thematic synthesis · byte 55171
  - context: Agrobiodiversity is context dependent, so even in the situations of corporate top-down efforts for incentivizing sustainability in supply chains, their implementation requires local knowledge in which multiple stakeholders from agriculture and the food industry can benefit from working with locally based researchers and organizations (Oliveira da Silva et al., 2024).

### A3  url / image span — 8

**SPECIFIED — A3 exclusion span**

- `(https://cdn.mathpix.com/cropped/8cf4cb26-15d6-435d-9582-4c99238a5325-09.jpg?height=1730&width=1764&top_left_y=218&top_l`
  - 43338825 · Follower Characteristics as Control Variables · byte 44906
  - context: One item stemmed from the neuroticism subscale of the Big Six (Ashton et al., 2004) and three were taken from the BFI (John and Srivastava, 1999) ( 1 = strongly disagree to 5 = strongly agree; $\alpha=0.89$ ). ![](https://cdn.mathpix.com/cropped/8cf4cb26-15d6-435d-9582-4c99238a5325-09.jpg?height=1730&width=1764&top_left_y=218&top_left_x=152)
- `(https://cdn.mathpix.com/cropped/8cf4cb26-15d6-435d-9582-4c99238a5325-12.jpg?height=1732&width=1764&top_left_y=218&top_l`
  - 43338825 · Overview · byte 58755
  - context: Hence, the field study complements our experiments by adding ecological validity to our results. ![](https://cdn.mathpix.com/cropped/8cf4cb26-15d6-435d-9582-4c99238a5325-12.jpg?height=1732&width=1764&top_left_y=218&top_left_x=152)
- `(https://cdn.mathpix.com/cropped/8cf4cb26-15d6-435d-9582-4c99238a5325-13.jpg?height=2077&width=740&top_left_y=235&top_le`
  - 43338825 · Participants · byte 60155
  - context: ![](https://cdn.mathpix.com/cropped/8cf4cb26-15d6-435d-9582-4c99238a5325-13.jpg?height=2077&width=740&top_left_y=235&top_left_x=211) FIGURE 4 | (A-E) Moderated mediation of intention and perception of abusive supervision on the relationship between abusive supervision behavior and reactions (including negative affectivity as control, only abusive vignettes) Study 2. ${ }^{\dagger} p<0.10$ (2-taile …
- `(https://cdn.mathpix.com/cropped/8cf4cb26-15d6-435d-9582-4c99238a5325-14.jpg?height=588&width=1091&top_left_y=1760&top_l`
  - 43338825 · Preliminary Results: Comparison Between Studies · byte 64317
  - context: ![](https://cdn.mathpix.com/cropped/8cf4cb26-15d6-435d-9582-4c99238a5325-14.jpg?height=588&width=1091&top_left_y=1760&top_left_x=484) FIGURE 7 | Interaction between abusive supervision and attribution to the supervisor on prohibitive voice (Study 2).
- `(https://cdn.mathpix.com/cropped/e9b624dc-5b70-48df-a039-d33fa4c44ac9-11.jpg?height=729&width=1281&top_left_y=1703&top_l`
  - 50408397 · Results and Discussion Study 2 · byte 49300
  - context: FIGURE 2 Belief in the CSP-CFP Link in the Three Experimental Conditions, Study 2 ![](https://cdn.mathpix.com/cropped/e9b624dc-5b70-48df-a039-d33fa4c44ac9-11.jpg?height=729&width=1281&top_left_y=1703&top_left_x=391)
- `(https://cdn.mathpix.com/cropped/37f86843-5741-4dce-9477-c372dae9588d-22.jpg?height=329&width=1181&top_left_y=1914&top_l`
  - ad1e3ff9 · Independent variables · byte 43003
  - context: Clustering in binary directed networks ![](https://cdn.mathpix.com/cropped/37f86843-5741-4dce-9477-c372dae9588d-22.jpg?height=329&width=1181&top_left_y=1914&top_left_x=429)
- `(https://cdn.mathpix.com/cropped/f2e0b348-3ade-43b7-974f-92a56b70ac55-03.jpg?height=1214&width=1684&top_left_y=361&top_l`
  - e1b418a4 · Abstract · byte 7969
  - context: FIGURE 1 Hypothesized Model ![](https://cdn.mathpix.com/cropped/f2e0b348-3ade-43b7-974f-92a56b70ac55-03.jpg?height=1214&width=1684&top_left_y=361&top_left_x=187)
- `(https://cdn.mathpix.com/cropped/f2e0b348-3ade-43b7-974f-92a56b70ac55-18.jpg?height=1214&width=1684&top_left_y=361&top_l`
  - e1b418a4 · Test of Hypotheses · byte 73315
  - context: FIGURE 2 Multilevel Path Analyses Results ![](https://cdn.mathpix.com/cropped/f2e0b348-3ade-43b7-974f-92a56b70ac55-18.jpg?height=1214&width=1684&top_left_y=361&top_left_x=189)

### et-al punctuation — 8

**LIMITATION — malformed input**

- `Schmidt et al., (2017)`
  - ad1e3ff9 · Control variables · byte 48111
  - context: The clustering score considers the number of closed triads formed by supply chain member $i$ expressed as a function of the possible number of closed-triads it could form. | Adapted from Fagiolo, 2007 as per Kolaczyk and Csárdi, 2014, p. 82. | | (4) | SCGeographicalH | Supply chain geographical heterogeneity | Bloomberg SPLC | Categorical heterogeneity score where each category $k$ represents a di …
- `(Choi at al., 2001)`
  - ad1e3ff9 · Managerial implications · byte 71354
  - context: Our research model considers variables that are not entirely within the control of practitioners; supply chain structure is time-invariant in the short term, and it is partially subject to an emergent process (Choi at al., 2001).
- `Whiteman et al, 2013`
  - c1d56945 · Regenerative sustainability · byte 6838
  - context: Hence, regeneration should be understood and studied considering place, because it is where social systems interact with natural ecosystems (Guthey et al., 2014; Whiteman et al, 2013).
- `Slawinski, et al., 2021`
  - c1d56945 · Regenerative organizing and sustainable supply chain management · byte 9405
  - context: Regenerative organizations are ecologically embedded in the place and are designed with the purpose of regenerating degraded living ecosystems and building resilience in communities (Muñoz and Branzei, 2011; Slawinski, et al., 2021).
- `Gualandris, et al., 2024`
  - c1d56945 · Regenerative organizing and sustainable supply chain management · byte 9753
  - context: In a similar vein, regenerative supply chains are defined as "inter-organizational networks that sense and embrace surrounding living systems, aligning their decision-making and actions to these systems' structures and dynamics in a way that allows for such systems to gain strength, build resilience, and sustain life" (Gualandris, et al., 2024; p.56).
- `Garrett et al, 2017`
  - c1d56945 · Practices · byte 23405
  - context: It refers to farming practices that promote diversity of plants, species, and micro-organisms, which have effects on the improvement of soil nutrients and water retention, making crops resilient to droughts, pest, and weeds; also, improving crop productivity and providing a diversified source of incomes for farmers, which also impacts food security of smallholder farmers (Garrett et al, 2017; Macf …
- `Esquivel, et al 2021`
  - c1d56945 · Stakeholders' collective actions · byte 31300
  - context: Community organizing also entails farmer-to-farmer or campesino knowledge exchange networks in which best practices are shared (Esquivel, et al 2021; Vanlauwe et al., 2019).
- `Ali., 2024`
  - c1d56945 · Socio-ecological measurement · byte 67673
  - context: The main challenges stem from comprehensive metrics encompassing ecological, social and economic indicators (Ali., 2024; Le et al., 2023), supply chain-wide biodiversity indices (Salmi et al., 2023), and standardization of agronomic criteria like nutrient efficiency (Tripathi et al., 2024).

### institutional author — 6

**NEW GRAMMAR — institutional extraction path**

- `(International Monetary Fund, 2022)`
  - 849f8fc6 · Introduction · byte 7987
  - context: Global growth is projected to be just 3.6 per cent in 2022, 0.8 percentage points lower than the January 2022 projections (International Monetary Fund, 2022).
- `(Population Pyramid, 2022)`
  - 849f8fc6 · Introduction · byte 10858
  - context: Spain has a population of 47 million and a half (Population Pyramid, 2022) and a GDP per capita of 30 thousand US dollars.
- `(National Statistical Institute, 2022)`
  - 849f8fc6 · Introduction · byte 11318
  - context: Spain has 3,430,663 enterprises, with 95.8\% of them employing less than nine workers and $3.95 \%$ between 10 and 99 workers (National Statistical Institute, 2022).
- `World Bank (2016)`
  - ad1e3ff9 · Control variables · byte 54012
  - context: This variable is based on the average of six indicators ranging from political stability to government effectiveness, as provided by the World Bank (2016).
- `(Ellen MacArthur, 2024)`
  - c1d56945 · Regenerative sustainability · byte 7170
  - context: The Ellen MacArthur Foundation defined circular economy as restorative and regenerative system by design, based on three principles: eliminate waste and pollution, circulate products and materials, and regenerate nature (Ellen MacArthur, 2024).
- `(University of Pretoria 2021a)`
  - ea07e5f5 · Data collection · byte 31135
  - context: All interview- and probing- questions served as the building blocks for the research questions and were carefully formulated as open-ended questions to ensure that conversations were stimulated (University of Pretoria 2021a).

### coordinated narrative — 6

**NEW GRAMMAR — author after 'and'**

- `and Sauer and Seuring (2023)`
  - c1d56945 · Method · byte 11327
  - context: We conducted a systematic literature review (SLR) following the methodological guidelines provided by Durach et al. (2017) and Sauer and Seuring (2023), further aligned with recent literature in supply chain management (e.g., Ateş and Luzzini, 2024; Marculetiu et al., 2023).
- `and Müller (2008)`
  - c1d56945 · Discussion · byte 57002
  - context: To this end, we selected two of the most influential frameworks-Seuring and Müller (2008) and Pagell and Wu (2009)-and structured our discussion around integrating our key results within 27 these models.
- `and Pagell and Wu (2009)`
  - c1d56945 · Discussion · byte 57020
  - context: To this end, we selected two of the most influential frameworks-Seuring and Müller (2008) and Pagell and Wu (2009)-and structured our discussion around integrating our key results within 27 these models.
- `and Layton and Muraven (2014)`
  - e1b418a4 · Supervisor Self-Control as a Predictor of Justice Variability · byte 50582
  - context: For example, Zabelina, Robinson, and Anicha (2007) demonstrated that individuals high in self-control were more consistent in their personality traits during their daily lives, and Layton and Muraven (2014) demonstrated that self-control was associated with greater emotional stability.
- `and Ohly, Sonnentag, Niessen, and Zapf (2010)`
  - e1b418a4 · Analysis · byte 62318
  - context: Following the suggestions of Hofmann and Gavin (1998) and Ohly, Sonnentag, Niessen, and Zapf (2010), we centered exogenous variables measured at the daily level (Level 1) around each person's mean ("group-mean centering") and grand-mean centered individual-level variables (Level 2).
- `and Scott et al. (2012)`
  - e1b418a4 · Justice Variability · byte 64404
  - context: Next, in accordance with Fleeson (2001) and Scott et al. (2012), we compared the average of each person's standard deviation in justice to the overall standard deviation in average justice over the threeweek period "to determine whether individuals differed from themselves over time as much as they differed from one another at the average level" (Scott et al., 2012: 913).

### forename-first / journal — 4

**LIMITATION — X-07, out of profile**

- `César Martínez Morán & Gisela Delfino (2023)`
  - 849f8fc6 · front matter · byte 218
  - context: To cite this article: Jesús Labrador Fernández, Pedro César Martínez Morán & Gisela Delfino (2023) Lessons learned in people management after COVID-19 crisis.
- `Gisela Delfino, Cogent Business & Management (2023)`
  - 849f8fc6 · Citation information · byte 56677
  - context: Jesús Labrador Fernández, Pedro César Martínez Morán & Gisela Delfino, Cogent Business & Management (2023), 10: 2275370.
- `Bornman & L. Steenkamp (2023)`
  - ea07e5f5 · front matter · byte 158
  - context: Bornman & L. Steenkamp (2023) The impact of a pandemic on entrepreneurial behaviour: A qualitative study of wedding vendors, Cogent Business & Management, 10:2, 2199908, DOI: 10.1080/23311975.2023.2199908
- `L. Steenkamp, Cogent Business & Management (2023)`
  - ea07e5f5 · Citation information · byte 63547
  - context: Bornman & L. Steenkamp, Cogent Business & Management (2023), 10: 2199908.

### wrong separator — 4

**LIMITATION — malformed input**

- `(da Silva et al., 2024: Wezel et al., 2016)`
  - c1d56945 · Stakeholders' collective actions · byte 28548
  - context: This subcode includes local networks of innovation, which refers to territorial innovation process, including social and cultural networks for the adoption of agroecological practices (Duru et al., 2015; Jordan et al., 2016); grass root, bottom-up innovation initiatives in which farmers and local communities engage in knowledge sharing and co-creation of solutions for their production needs (da Si …
- `Resque et al., 2019, Sam, 2018`
  - c1d56945 · Stakeholders' collective actions · byte 30485
  - context: Cooperatives provide a platform for farmers to participate in decision-making, strengthen their agency capability, and gain better access to markets (Levidow, 2023; Resque et al., 2019, Sam, 2018); also act as intermediaries between producers and buyers (including public procurement), ensuring quality, managing contracts, and reducing transaction costs (Bisht et al., 2020; Esquivel et al., 2021; S …
- `(Buor 2022, Debrot, 2020, Dudley and Alexander, 2017)`
  - c1d56945 · Outcomes · byte 45759
  - context: Regarding social outcomes, the analyzed papers studied the improvement of rural household's incomes, and whether agroecological crops diversified the sources of incomes (Buor 2022, Debrot, 2020, Dudley and Alexander, 2017); the enhancement on food security (i.e. availability, affordability, and access), improving nutritional quality and diversity of diets (Bisht, 2019, Speich); the promotion of so …
- `(Bisht, 2019, Speich)`
  - c1d56945 · Outcomes · byte 45948
  - context: Regarding social outcomes, the analyzed papers studied the improvement of rural household's incomes, and whether agroecological crops diversified the sources of incomes (Buor 2022, Debrot, 2020, Dudley and Alexander, 2017); the enhancement on food security (i.e. availability, affordability, and access), improving nutritional quality and diversity of diets (Bisht, 2019, Speich); the promotion of so …

### math / LaTeX — 3

**SPECIFIED — A3 widened to math**

- `\alpha=0.96`
  - 43338825 · Reactions to Abusive Supervision (T2) · byte 46484
  - context: For loyalty, we used the 5 items supervisor commitment scale $(\alpha=0.96 ; 1=$ never to 5 = frequently; Felfe et al., 2006).
- `1=$ never to 5 = frequently`
  - 43338825 · Reactions to Abusive Supervision (T2) · byte 46498
  - context: For loyalty, we used the 5 items supervisor commitment scale $(\alpha=0.96 ; 1=$ never to 5 = frequently; Felfe et al., 2006).
- `+1 and -1 SD`
  - e1b418a4 · Test of Hypotheses · byte 68684
  - context: To explore the form of this cross-level interaction, we plotted the relationship at conditional values of justice variability (+1 and -1 SD; Cohen, Cohen, West, & Aiken, 2003).

### artifact / non-citation — 3

**NOT A CITATION — conversion artefact**

- `MBSR`
  - 4918fd7d · Mindfulness · byte 15211
  - context: Research has shown that mindfulness programs, such as MindfulnessBased Stress Reduction (MBSR; Kabat-Zinn, 1982), benefit mental and physical health in clinical populations (Baer, 2003; Grossman, Niemann, Schmidt, & Walach, 2004; Hofmann, Sawyer, Witt, & Oh, 2010).
- `(ECP_150 03_08_2014_A2 OZL)`
  - 4918fd7d · Design and Procedure Study 2 · byte 50950
  - context: The study was approved by the local ethical review board (ECP_150 03_08_2014_A2 OZL).
- `McMindfulness`
  - 4918fd7d · A Final Note · byte 80801
  - context: Several authors have criticized the shallow and popularized version of mindfulness (McMindfulness; Purser & Loy, 2013) for lacking the inherently genuine and ethical foundations that defined the original traditions.

### missing comma before year — 2

**LIMITATION — malformed input**

- `(Van Quaquebeke 2016)`
  - 4918fd7d · Sample and Procedure Study 1 · byte 27536
  - context: This study was part of a larger data collection effort on leader mental health (Van Quaquebeke 2016), but used different variables.
- `(Lu and Shang 2017)`
  - ad1e3ff9 · Supply chain structural dimensions · byte 11889
  - context: More recent studies recognize the importance of dimensions like centrality and brokerage at a firm level of analysis, and eliminative and cooperative complexity at a supply base level of analysis (Lu and Shang 2017).

### colon page-locator — 2

**NOT A CITATION — trailing prose after locator**

- `(El Akremi et al., 2015: 2)`
  - 50408397 · Measures · byte 60962
  - context: The items on this scale describe various "actions and policies designed to enhance the welfare of various stakeholder groups" (El Akremi et al., 2015: 2).
- `Indeed, Lind and van den Bos (2002: 196)`
  - e1b418a4 · Limitations · byte 94883
  - context: Indeed, Lind and van den Bos (2002: 196) posited that a global impression of fair treatment "is the key to managing uncertainty."

### B6  compact year-suffix — 2

**SPECIFIED — B6**

- `(Sharma et al., 2019a,b)`
  - ad1e3ff9 · Data collection and cleaning process · byte 33482
  - context: Similar to recent studies (Sharma et al., 2019a,b), we were able to overcome this challenge by randomly sampling a limited number of focal firms and then using multiple Bloomberg terminals and an efficient data collection procedure.
- `Sharma et al., 2019a,b`
  - ad1e3ff9 · Limitations and future developments · byte 76902
  - context: Moreover, several studies show that supply chain structure is time-invariant in the short term (Osadchiy et al., 2015; Sharma et al., 2019a,b).

### all-caps surname — 2

**LIMITATION — already registered**

- `(FAO, 2018)`
  - c1d56945 · Regenerative organizing and sustainable supply chain management · byte 8742
  - context: The elements of agroecology include issues that go from circular and solidarity economy, knowledge sharing between actors in a territory, responsible governance, synergies between elements of an ecosystem and its resilience (FAO, 2018).
- `(FAO, 2005)`
  - c1d56945 · Practices · byte 23017
  - context: According to FAO, agrobiodiversity is the variety and variability of animals, plants and micro-organisms that are used directly or indirectly for food and agriculture, including crops, livestock, forestry and fisheries (FAO, 2005).

### bare locator — 2

**NOT A CITATION — detached locator**

- `p.56`
  - c1d56945 · Regenerative organizing and sustainable supply chain management · byte 9779
  - context: In a similar vein, regenerative supply chains are defined as "inter-organizational networks that sense and embrace surrounding living systems, aligning their decision-making and actions to these systems' structures and dynamics in a way that allows for such systems to gain strength, build resilience, and sustain life" (Gualandris, et al., 2024; p.56).
- `P.923`
  - c1d56945 · Supplier continuity · byte 66966
  - context: To reach this scale, "developing country governments should work with multilateral agencies, local governments and NGOs to identify and combine natural landscape projects from various localities and regions into a single nation-wide investment portfolio" (Barbier, 2022; P.923).

### prose-embedded citation — 1

**LIMITATION — prose-embedded**

- `(conservation of resource theory, Hobfoll, 1989, and ego-depletion, Baumeister et al., 1998)`
  - 43338825 · FOLLOWER CHARACTERISTICS AS CONTROL VARIABLES · byte 25921
  - context: The more followers feel stressed, the more likely they are to perceive abusive supervision (e.g., Tepper, 2000; Chen and Kao, 2009) and react more strongly toward abusive behavior due to their lack of resources to self-regulate (conservation of resource theory, Hobfoll, 1989, and ego-depletion, Baumeister et al., 1998).

### particle case — 1

**NEW GRAMMAR — particle case-folding**

- `(Da silva et al., 2017)`
  - c1d56945 · Regulation · byte 37952
  - context: Forest codes have also had a negative effect on the implementation of restoration projects, for instance in Brazil forest codes prohibit the native seed collection in protected areas, which hampers the inclusion of high-conservation-value species in restoration projects (Da silva et al., 2017).

### non-numeric year — 1

**LIMITATION — malformed input**

- `(Smith, Weed, & Ramsay, 2005-present)`
  - e1b418a4 · Abstract · byte 2573
  - context: That would make my life a lot easier!" (Smith, Weed, & Ramsay, 2005-present) The above quotes are from celebrity chef Gordon Ramsay.

### possessive narrative — 1

**NEW GRAMMAR — possessive normalisation**

- `and Fotiadis's (2018)`
  - ea07e5f5 · Theoretical implications · byte 57855
  - context: This study is in contrast to Samoedra et al. (2021) and Fotiadis's (2018) since these authors focused on paid advertising, where, according to the participants of this study word-of-mouth is the most popular method of advertising.

---

## 2. Unresolved references (59)

### orphan_line — 48

A bibliography line the entry grammar could not start. Most are the second
line of a wrapped entry, so the entry above it parsed and this is its tail.

- 43338825 · byte 95092
  - `from psycholexical studies in seven languages. J. Pers. Soc. Psychol. 86, 356-366. doi: 10.1037/0022-3514.86.2.356`
- 43338825 · byte 105648
  - `Copyright © 2018 Schyns, Felfe and Schilling. This is an open-access article distributed under the terms of the Creative Commons Attribution License (CC BY). The use, distribution or reproduction in o`
- 43338825 · byte 106145
  - `[^0]:    ${ }^{1}$ Since all data reported here were collected using panel providers, no informed consent forms were used. Participants in panel studies can chose to take part in studies for a small r`
- 43338825 · byte 106750
  - `[^1]:    ${ }^{2}$ We conducted the same manipulation check in Study 1 with comparable results (see Table 1). The reliability for liking was $\alpha=0.97$. For Generalized Leadership Impression, the r`
- 43338825 · byte 106981
  - `[^2]:    ${ }^{3}$ Testing the model without control variables does not change the results.`
- 43338825 · byte 107074
  - `[^3]:    ${ }^{4}$ In order to plot the interaction, we conducted moderated regressions using the vignettes as a control variable.`
- 43338825 · byte 107206
  - `[^4]:    ${ }^{*} p<0.05$ (2-tailed), ${ }^{* *} p<0.01$ (2-tailed).`
- 4918fd7d · byte 112686
  - `Publisher's Note Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations.`
- 4918fd7d · byte 112824
  - `[^0]:    Annika Nübold`
- 4918fd7d · byte 112851
  - `a.nubold@maastrichtuniversity.nl`
- 4918fd7d · byte 112888
  - `${ }^{1}$ Faculty of Psychology and Neuroscience, Department of Work and Social Psychology, Maastricht University, P.O. Box 616, 6200 MD Maastricht, The Netherlands`
- 4918fd7d · byte 113057
  - `${ }^{2}$ Management Department, Kühne Logistics University, Hamburg, Germany`
- 4918fd7d · byte 113135
  - `[^1]:    ${ }^{\mathrm{a}}$ Gender: 0 = female, 1 = male`
- 4918fd7d · byte 113196
  - `${ }^{\mathrm{b}}$ Coding: 0 = control group, 1= intervention group`
- 4918fd7d · byte 113268
  - `$\dagger p<.10,{ }^{*} p<.05,{ }^{* *} p<.01,{ }^{* * *} p<.001$ (two-tailed)`
- 50408397 · byte 92176
  - `El Akremi, A., Gond, J.-P., Swaen, V., De Roeck, K., & Igalens, J. 2015. How do employees perceive corporate responsibility? Development and validation of`
- 50408397 · byte 92331
  - `a multidimensional corporate stakeholder responsibility scale. Journal of Management. https://doi.org/10.1177/0149206315569311.`
- 50408397 · byte 107090
  - `Sebastian Hafenbrädl (shafenbraedl@iese.edu) joined IESE Business School as an assistant professor, after conducting postdoctoral studies at the School of Management, Yale University. He received his `
- 50408397 · byte 107602
  - `Daniel Waeger (dwaeger@wlu.ca) is an assistant professor at Wilfrid Laurier University. Before joining Wilfrid Laurier, Daniel was an assistant professor at the University of Amsterdam. He received hi`
- 50408397 · byte 107998
  - `empirical phenomena such as corporate responsibility and corporate governance.`
- 50408397 · byte 108077
  - `![](https://cdn.mathpix.com/cropped/e9b624dc-5b70-48df-a039-d33fa4c44ac9-25.jpg?height=42&width=428&top_left_y=372&top_left_x=1285)`
- ad1e3ff9 · byte 95364
  - `Agarwal N., Lim M., Wigand R. (eds) Online Collective Action. Lecture Notes in Social Networks. Springer, Vienna.`
- ad1e3ff9 · byte 99770
  - `[^0]:    ${ }^{1}$ To cross-validate our customer/supplier lists from Bloomberg SPLC we used Compustat's segment database and the Thomson Reuters value chains database. A comparison between data from `
- ad1e3ff9 · byte 100156
  - `[^1]:    ${ }^{2}$ We conducted a power analysis, as proposed by Cohen (1988) for the F-test, assuming a medium effect size (0.15) for nine controls and four predictors and a desired significance leve`
- ad1e3ff9 · byte 100368
  - `[^2]:    ${ }^{3}$ Harley-Davidson (Automobiles and Components), Keyence Corp. (Technology Hardware and Equipment), Asahi (Food, Beverage, and Tobacco), and some other focal firms in our final sample `
- ad1e3ff9 · byte 100788
  - `[^3]:    ${ }^{4}$ The Bloomberg ESG database predominantly covers public firms with medium and large market capitalization ( $\geq$ US\$2billion). In this database, firms that do not disclose anythin`
- ad1e3ff9 · byte 101494
  - `[^4]:    ${ }^{5} E$ counts the number of "edges" or contractual ties in a given supply chain $j$. The adopted density score treats each extended supply chain $j$ as a binary directed network where re`
- ad1e3ff9 · byte 101785
  - `[^5]:    ${ }^{6}$ An advantage of the adopted measure is that it accounts for false open triads where two supply chain members are connected by a reciprocated tie but cannot possibly form any closed `
- ad1e3ff9 · byte 102112
  - `[^6]:    ${ }^{7}$ The entropy-based measure of heterogeneity consists of the sum of $p_{\mathrm{i}} * \log \left(p_{\mathrm{i}}\right)$, where $p$ is the fraction of suppliers represented in a specif`
- ad1e3ff9 · byte 102386
  - `[^7]:    ${ }^{8}$ This variable measures the average percentage of known revenues per supplier $i$ in a given supply chain $j$ ( mean $=24.21 \% ; \min =8.12 \% ; \max =39.1 \%$ ).`
- ad1e3ff9 · byte 102569
  - `[^8]:    ${ }^{9}$ The variable supply chain relevance measures the average portion of revenues that suppliers $i$ in a given supply chain $j$ receive from supply chain members in the same supply chai`
- c1d56945 · byte 76819
  - `FAO, 2018. The 10 Elements of Agroecology. https://www.fao.org/agroecology/overview/overview10elements/en/`
- e1b418a4 · byte 123404
  - `Fadel K. Matta (fmatta@uga.edu) is an assistant professor in the Department of Management at the University of Georgia's Terry College of Business. He received his PhD from Michigan State University, `
- e1b418a4 · byte 123786
  - `Brent A. Scott (scott@broad.msu.edu) is an associate professor of management at the Eli Broad College of Business at Michigan State University. He received his PhD from the University of Florida. His `
- e1b418a4 · byte 124081
  - `Jason A. Colquitt (colq@uga.edu) is the William Harry Willson Distinguished Chair in the Department of Management at the University of Georgia's Terry College of Business. He received his PhD from Mic`
- e1b418a4 · byte 124491
  - `Joel Koopman (jkoopman@mays.tamu.edu) is an assistant professor of management in the Mays Business School at Texas A&M University. He received his PhD from Michigan State University. His research inte`
- e1b418a4 · byte 124777
  - `Liana G. Passantino (passantino@bus.msu.edu) is a doctoral candidate in organizational behavior and human resource management at the Eli Broad College of Business, Michigan State University. Her resea`
- e1b418a4 · byte 125082
  - `![](https://cdn.mathpix.com/cropped/f2e0b348-3ade-43b7-974f-92a56b70ac55-28.jpg?height=42&width=426&top_left_y=1819&top_left_x=1285)`
- e1b418a4 · byte 125216
  - `Copyright of Academy of Management Journal is the property of Academy of Management and its content may not be copied or emailed to multiple sites or posted to a listserv without the copyright holder'`
- e1b418a4 · byte 125522
  - `[^0]:    ${ }^{1}$ Despite the task being challenging, our instructions (available upon request from the first author) made it clear that the task involved skill (rather than luck), and we informed pa`
- e1b418a4 · byte 125940
  - `[^1]:    ${ }^{2}$ As suggested by an anonymous reviewer, we reanalyzed our data including the 36 participants who guessed the supervisor was fictitious and/or claimed they did not try on the task. Al`
- e1b418a4 · byte 127286
  - `[^2]:    ${ }^{3}$ An anonymous reviewer questioned whether these statements could reflect overall positive versus negative feedback about participant performance. To address this, we conducted a supp`
- e1b418a4 · byte 128584
  - `[^3]:    ${ }^{4}$ Although our theorizing focuses on overall fairness, we also assessed interpersonal justice and interpersonal injustice using the Colquitt et al. (2015) scales. The results for the `
- e1b418a4 · byte 129004
  - `[^4]:    ${ }^{5}$ We thank an anonymous reviewer for this suggestion.`
- e1b418a4 · byte 129079
  - `${ }^{6}$ Although our theorizing focuses on overall fairness, we also assessed interpersonal justice and interpersonal injustice using the Colquitt et al. (2015) scales. The Manipulation Check Study `
- e1b418a4 · byte 129487
  - `[^5]:    ${ }^{7}$ We collapsed across the two consistent conditions in the one-way ANOVA because our hypothesis centered on the effects of variably fair treatment versus consistent treatment (regardl`
- e1b418a4 · byte 129851
  - `[^6]:    ${ }^{8}$ We also conducted four additional analyses to further probe these relationships. First, we conducted an exploratory analysis to test the three-way interaction between uncertainty, a`
- ea07e5f5 · byte 66199
  - `Covid-19 pandemic. Business and Society Review, 127 (S1), 223-251.`

### entry_start_grammar — 11

The line looks like an entry start but does not satisfy `ENTRY_START`.

- 4918fd7d · byte 107097
  - `Pircher Verdorfer, A. (2016). Examining mindfulness and its relations to humility, motivation to lead, and actual servant leadership behaviors. Mindfulness, 7(4), 950-961. https://doi.org/10.1007/s126`
- 5da73cf4 · byte 61478
  - `Dobrajska, M & Billinger, S & Karim, S. (2015). Delegation within hierarchies: How information processing and knowledge characteristics influence the allocation of formal and real decision authority. `
- 5da73cf4 · byte 62250
  - `McCann, J & Gilmore, Thomas. (1983). Diagnosing organizational decision making through responsibility charting. Sloan management review. 24. 3-15.`
- 849f8fc6 · byte 60816
  - `Expansion. (2022). PIB de España - Producto Interior Bruto [Spain's GDP - Gross Domestic Product]. https://datos macro.expansion.com/pib/espana\#:~:text=Espa\% C3\%B1a\%3A\%20El\%20PIB\%20ascendi\%C3\`
- 849f8fc6 · byte 62783
  - `International Monetary Fund. (2022, April). War sets back the global recovery. https://www.imf.org/en/ Publications/WEO/Issues/2022/04/19/worldeconomic-outlook-april-2022`
- 849f8fc6 · byte 65043
  - `National Statistical Institute. (2022). Active companies by economic sector January 1. 2022. https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736160707&menu=ultiDatos&idp=1254`
- 849f8fc6 · byte 66583
  - `Population Pyramid. (2022). Spain. https://www.popula tionpyramid.net/es/espa\�\�a/2022/`
- ad1e3ff9 · byte 84681
  - `Bloomberg. (2011). Supply Chain on Bloomberg. Retrieved December 7, 2018, from https://business.library.emory.edu/documents/faq-handouts/bloomberg-splc.pdf.`
- ad1e3ff9 · byte 84838
  - `Bloomberg. (2013). Bloomberg Supply Chain Algorithm: Providing insight into a company relationships. Retrieved December 7, 2018, from https://kenan-flagler.instructure.com/files/54372815.`
- ad1e3ff9 · byte 95478
  - `RepRisk (2016). RepRisk Scope, Process and Metrics. Available at https://www.reprisk.com/our-approach\#risk-metrics. Accessed 11 Dec 2018.`
- ad1e3ff9 · byte 99453
  - `World Bank. (2016). Available at: https://datacatalog.worldbank.org/dataset/worldwidegovernance-indicators. Accessed 12 December 2018.`

---

## 3. missing_reference (36)

The citation parsed cleanly. Nothing in the bibliography carries its key.
Either the paper is genuinely missing the entry, or our reference side missed it.

```text
paper      citation_key                        occ  example
43338825   tepper's|2000                         3  Tepper's (2000)
4918fd7d   boyatzis|2005                         1  Boyatzis & McKee, 2005
4918fd7d   colquitt's|2001                       1  Colquitt's (2001)
4918fd7d   donaldsonfeilder|2018                 1  DonaldsonFeilder, Lewis, & Yarker, 2018
4918fd7d   george|2010                           1  George, 2010
4918fd7d   kabat-zinn|2011                       1  Kabat-Zinn, 2011
4918fd7d   kabatzinn|1982                        1  KabatZinn, 1982
4918fd7d   kabatzinn|2003                        1  KabatZinn, 2003
50408397   gond|2015                             1  Gond, Swaen, De Roeck, and Igalens (2015)
50408397   hambrick's|2007                       3  Hambrick's (2007)
5da73cf4   dobrajska|2015                        7  Dobrajska et al., 2015
5da73cf4   mccann|1983                           3  McCann & Gilmore, 1983
849f8fc6   expansion|2022                        1  Expansion, 2022
ad1e3ff9   bartko's|1976                         1  Bartko's (1976)
ad1e3ff9   centola|2013                          3  Centola, 2013
ad1e3ff9   darnall|2009                          1  Darnall et al., 2009
ad1e3ff9   den brink|2004                        1  den Brink and Van der Woerd (2004)
ad1e3ff9   fine's|1998                           1  Fine's (1998)
ad1e3ff9   fu|2016                               1  Fu and Shumate, 2016
ad1e3ff9   marquis|2018                          1  Marquis et al., 2018
ad1e3ff9   mcgraw|1996                           1  McGraw and Wong's (1996)
ad1e3ff9   reprisk|2016                          1  RepRisk (2016)
ad1e3ff9   wenger|1998                           1  Wenger, 1998
c1d56945   barbieri|2023                         1  Barbieri et al., 2023
c1d56945   barrios|2020                          2  Barrios et al., 2020
c1d56945   de la cruz|2021                       2  De La Cruz and Dessein, 2021
c1d56945   de santana|2023                       5  de Santana et al., 2023
c1d56945   du plessis|2011                       1  du Plessis and Cole, 2011
c1d56945   glaser|2024                           1  Glaser et al., 2024
c1d56945   guthey|2014                           1  Guthey et al., 2014
c1d56945   muñoz|2011                            1  Muñoz and Branzei, 2011
c1d56945   salliou|2019                          1  Salliou, 2019
e1b418a4   jorm|1999                             1  Jorm, Christensen, Korten, Jacomb, and Rodgers (1999)
e1b418a4   leventhal's|1980                      3  Leventhal's (1980)
e1b418a4   workman|2012                          1  Workman, Van Dijke, and De Cremer (2012)
ea07e5f5   fotiadis's|2018                       1  Fotiadis's (2018)
```
---

## 4. uncited_reference (33)

The entry parsed. No citation matched it. **This is the one that finds our own
silent misses**, so it is worth reading against the paper.

- **baumeister|1998** · 43338825
  - Baumeister, R. F., Bratslavsky, E., Muraven, M., and Tice, D. M. (1998). Ego depletion: is the active self a limited resource? J. Pers. Soc. Psychol. 74, 1252-1265. doi: 10.1037/0022-3514.74. 5.1252
- **harvey|2014** · 43338825
  - Harvey, P., Madison, K., Martinko, M., Crook, T. R., and Crook, T. A. (2014). Attribution theory in the organizational sciences: the road traveled and the path ahead. Acad. Manage. Perspect. 28, 128-146. doi: 10.5465/amp. 2012.0175
- **hobfoll|1989** · 43338825
  - Hobfoll, S. E. (1989). Conservation of resources: a new attempt at conceptualizing stress. Am. Psychol. 44, 513-524. doi: 10.1037/0003-066X.44.3.513
- **martinko|2012** · 43338825
  - Martinko, M. J., Sikora, D., and Harvey, P. (2012). The relationship between attribution styles, LMX, and perceptions of abusive supervision. J. Leadersh. Organ. Stud. 19, 397-406. doi: 10.1177/1548051811435791
- **boyatzis|2014** · 4918fd7d
  - Boyatzis, R. E., & McKee, A. (2014). Resonant leadership: Renewing yourself and connecting with others through mindfulness, hope, and compassion. Boston, MA: Harvard Business School Press.
- **colquitt|2001** · 4918fd7d
  - Colquitt, J. A. (2001). On the dimensionality of organizational justice: A construct validation of a measure. Journal of Applied Psychology, 86(3), 386-400.
- **george|2007** · 4918fd7d
  - George, B., & Sims, P. (2007). True north: Discover your authentic leadership (1st ed.). San Fransico, CA: Jossey-Bass
- **hafenbrack|2014** · 4918fd7d
  - Hafenbrack, A. C., Kinias, Z., & Barsade, S. G. (2014). Debiasing the mind through meditation: Mindfulness and the sunk-cost bias. Psychological Science, 25(2), 369-376. https://doi.org/10.1177/0956797613503853.
- **harter|2002** · 4918fd7d
  - Harter, S. (2002). Authenticity. In C. R. Snyder, & S. Lopez (Eds.), Handbook of positive psychology (pp. 382-394).Oxford, UK: Oxford University Press.
- **iszatt-white|2018** · 4918fd7d
  - Iszatt-White, M., & Kempster, S. (2018). Authentic leadership: Getting back to the roots of the 'root construct'? International Journal of Management Reviews, 0(0), 1-14. https://doi.org/10.1111/ijmr. 12193.
- **kabat-zinn|2015** · 4918fd7d
  - Kabat-Zinn, J. (2015, October 20). Some reflections on the origins of MBSR, skillful means, and the trouble with maps. The GuardianRetrieved from http://www.theguardian.com/commentisfree/2015/oct/20/mindfulness-mental-health-potentialbenefits-uk. Accessed 24 O
- **oppenheimer|2009** · 4918fd7d
  - Oppenheimer, D. M., Meyvis, T., & Davidenko, N. (2009). Instructional manipulation checks: Detecting satisficing to increase statistical power. Journal of Experimental Social Psychology, 45(4), 867-872. https://doi.org/10.1016/j.jesp.2009.03.009.
- **van quaquebeke|2016** · 4918fd7d
  - Van Quaquebeke, N. (2016). Paranoia as an antecedent and consequence of getting ahead in organizations: Time-lagged effects between paranoid cognitions, self-monitoring, and changes in span of control. Frontiers in Psychology, 7(1446). https://doi.org/10.3389/
- **abildgaard|2016** · 5da73cf4
  - Abildgaard, J. S., Hasson, H., von Thiele Schwarz, U., Løvseth, L. T., Ala-Laurinaho, A., & Nielsen, K. (2016). Forms of knowledge useful for improving intervention work. Work & Stress, 30(3), 266-289. https:///doi.org/10.1177/0143831X17743576
- **bartko|1976** · ad1e3ff9
  - Bartko, J. (1976). On various intraclass correlation reliability coefficients. Psycological Bulletin, 83, 762-765.
- **cohen|1988** · ad1e3ff9
  - Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences. Lawrence Erlbaum.
- **dai|2020** · ad1e3ff9
  - Dai, R., Liang, H., & Ng, L. (2020). Socially responsible corporate customers. Journal of Financial Economics, https://doi.org/10.1016/j.jfineco.2020.01.003.
- **de villiers|2016** · ad1e3ff9
  - De Villiers, C., & Marques, A. (2016). Corporate social responsibility, country-level predispositions, and the consequences of choosing a level of disclosure. Accounting and Business Research, 46(2), 167-195.
- **fine|1998** · ad1e3ff9
  - Fine, C. (1998). Clockspeed: Winning Industry Control in the Age of Temporary Advantage. New York: Perseus Books.
- **wenger|2000** · ad1e3ff9
  - Wenger, E., and Snyder, W. (2000). Communities of practice: the organizational frontier. Harvard Business Review, 78(1), 139-145.
- **maurice-hammond|2023** · c1d56945
  - Maurice-Hammond, I., McAlvay, A., Mathews, D., Bosman, A., Morris, J., 2023. A ləkʷəŋən estuarine root garden: the case of Tl'chés. Economic Botany, 77 (4), 410-432.
- **sam|2018** · c1d56945
  - Sam, K., & Zabbey, N. (2018). Contaminated land and wetland remediation in Nigeria: opportunities for sustainable livelihood creation. Science of the Total Environment, 639, 1560-1573.
- **sauer|2023** · c1d56945
  - Sauer, P.C., Seuring, S., 2023. How to conduct systematic literature reviews in management research: a guide in 6 steps and 14 decisions. Review of Managerial Science, 17 (5), 1899-1933.
- **cook|1979** · e1b418a4
  - Cook, T. D., & Campbell, D. T. 1979. Quasiexperimentation: Design and analysis issues for field settings. Boston, MA: Houghton-Mifflin.
- **jin|2016** · e1b418a4
  - Jin, S., Seo, M.-G., & Shapiro, D. L. 2016. Do happy leaders lead better? Affective and attitudinal antecedents of transformational leadership. The Leadership Quarterly, 27: 64-84.
- **kline|2011** · e1b418a4
  - Kline, R. B. 2011. Principles and practice of structural equation modeling (3rd ed.). New York, NY: Guilford Press.
- **layton|2014** · e1b418a4
  - Layton, R. L., & Muraven, M. 2014. Self-control linked with restricted emotional extremes. Personality and Individual Differences, 58: 48-53.
- **mackinnon|1999** · e1b418a4
  - Mackinnon, A., Jorm, A. F., Christensen, H., Korten, A. E., Jacomb, P. A., & Rodgers, B. 1999. A short form of the positive and negative affect schedule: Evaluation of factorial validity and invariance across demographic variables in a community sample. Person
- **mayer|2012** · e1b418a4
  - Mayer, D. M., Thau, S., Workman, K. M., Van Dijke, M., & De Cremer, D. 2012. Leader mistreatment, employee hostility, and deviant behaviors: Integrating selfuncertainty and thwarted needs perspectives on deviance. Organizational Behavior and Human Decision Pro
- **ohly|2010** · e1b418a4
  - Ohly, S., Sonnentag, S., Niessen, C., & Zapf, D. 2010. Diary studies in organizational research. Journal of Personnel Psychology, 9: 79-93.
- **ou|2014** · e1b418a4
  - Ou, A. Y., Tsui, A. S., Kinicki, A. J., Waldman, D. A., Xiao, Z., & Song, L. J. 2014. Humble chief executive officers' connections to top management team integration and middle managers' responses. Administrative Science Quarterly, 59: 34-72.
- **smith|2005** · e1b418a4
  - Smith, A., Weed, K., & Ramsay, G. (Executive Producers) 2005-present. Hell's Kitchen [Television series]. Manchester, England; New York, NY: ITV Studios; ITV Studios America.
- **sonnentag|2003** · e1b418a4
  - Sonnentag, S., & Frese, M. 2003. Stress in organizations. In W. C. Borman, D. R. Ilgen, R. J. Klimoski (Eds.), Comprehensive handbook of psychology, vol. 12: Industrial and organizational psychology: 453-491. New York, NY: John Wiley & Sons, Inc.

---

## 5. ambiguous_citation (5)

One citation key, several bibliography entries. Neither matched nor missing.

- **felfe|2006** · 43338825 · entries [13, 15] · example `Felfe and Schyns, 2006`
- **hülsheger|2015** · 4918fd7d · entries [64, 66] · example `e.g., Hülsheger, Feinholdt, & Nübold, 2015`
- **newman|2014** · 50408397 · entries [82, 83] · example `Newman, Gorlin, & Dhar, 2014`
- **colquitt|2015** · e1b418a4 · entries [25, 26] · example `Colquitt & Rodell, 2015`
- **colquitt|2012** · e1b418a4 · entries [23, 24] · example `Colquitt, LePine, Piccolo, Zapata, and Rich (2012)`

## 6. possible_mismatch (5)

- ad1e3ff9 · citation `madison|2010` ↔ reference `madison|2009` · year_adjacent
- c1d56945 · citation `rodriguez|2024` ↔ reference `rodríguez|2024` · surname_edit_distance_1
- c1d56945 · citation `vieira|2021` ↔ reference `vieira|2022` · year_adjacent
- c1d56945 · citation `whiteman|2000` ↔ reference `whitman|2000` · surname_edit_distance_1
- e1b418a4 · citation `drachzahavy|2002` ↔ reference `drach-zahavy|2002` · surname_edit_distance_1

## 7. duplicate_reference_key (5)

A bibliography defect, not a reading of any citation.

- 43338825 · `felfe|2006` · entries [13, 15] · cited=True
- 4918fd7d · `hülsheger|2015` · entries [64, 66] · cited=True
- 50408397 · `newman|2014` · entries [82, 83] · cited=True
- e1b418a4 · `colquitt|2012` · entries [23, 24] · cited=True
- e1b418a4 · `colquitt|2015` · entries [25, 26] · cited=True
