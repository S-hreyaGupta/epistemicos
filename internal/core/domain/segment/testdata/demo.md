Citation: Al-Swidi AK, AI-Hakimi MA, AI Halbusi H, Al Harbi JA, AI-Hattami HM (2024) Does blockchain technology matter for supply chain resilience in dynamic environments? The role of supply chain integration. PLoS ONE 19(1): e0295452. https://doi.org/10.1371/journal. pone. 0295452

Editor: Kittisak Jermsittiparsert, University of City Island, CYPRUS

Received: June 20, 2023
Accepted: November 22, 2023
Published: January 5, 2024
Peer Review History: PLOS recognizes the benefits of transparency in the peer review process; therefore, we enable the publication of all of the content of peer review and author responses alongside final, published articles. The editorial history of this article is available here: https://doi.org/10.1371/journal.pone. 0295452

Copyright: © 2024 AI-Swidi et al. This is an open access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original author and source are credited.

Data Availability Statement: All relevant data are within the paper and its Supporting information files.

RESEARCH ARTICLE

# Does blockchain technology matter for supply chain resilience in dynamic environments? The role of supply chain integration 

Abdullah Kaid Al-Swidi ${ }^{\mathbf{1}}$, Mohammed A. Al-Hakimi ${ }^{\mathbf{2}}$ *, Hussam AI Halbusi ${ }^{\mathbf{3}}$, Jaithen Abdullah Al Harbi ${ }^{\mathbf{4}}$, Hamood Mohammed AI-Hattami ${ }^{\mathbf{5 , 6}}$<br>1 College of Business and Economics, Qatar University, Doha, Qatar, 2 Marketing and Production Department, Thamar University, Dhamar, Yemen, 3 Management Department, Ahmed Bin Mohammed Military College, Doha, Qatar, 4 Imam Mohamed bin Saud Islamic University, Riyad, Saudi Arabia, 5 College of Business Administration, A'Sharqiyah University (ASU), Ibra, Oman, 6 Department of Accounting, Faculty of Commerce and Economic, Hodeidah University, Al Hudaydah, Yemen<br>*alhakimi111@gmail.com


#### Abstract

This study aims to empirically investigate the effect of blockchain technology (BCT) adoption on supply chain resilience (SCR), with the mediating role of supply chain integration (SCI) and the crucial effect of environmental dynamism (ED) as a moderator. Based on data collected from firms operating in the automotive industry in India, the proposed model was tested using Partial Least Squares Structural Equations Modelling (PLS-SEM) via SmartPLS software. The empirical results showed a positive effect of BCT on SCI, which in turn affects SCR. Importantly, SCI acts as a full mediator in the BCT-SCR relationship, which is moderated by ED, that is, the effect of BCT on SCR via SCI is strong when ED is high. This study offers the groundwork for operationalizing BCT in a supply chain context. It also contributes to SCR research by investigating how SCI mediates the effect of BCT on SCR. In addition, this study found a moderating effect of ED on the relationship between BCT and SCI. These results provide insights to auto manufacturers on ways to enhance SCR and ensure safe supply chain operations.


## 1 Introduction

In the present interconnected global market, uncertainties and disturbances pose unpredictable challenges to long-term success and sustainability [1], which overthrow traditional management practices that focus only on stable conditions [2]. Each day, companies face disturbances that can undermine their operational efficiency. One example of those threats is the COVID-19 pandemic, which has recently negatively impacted the global and inter-twined supply networks [3, 4]. Due to the disturbances in the supply chains (SCs), the Indian automotive industry has suffered severe production disruptions in many factories [5]. The primary factor behind this impact was the heavy reliance of India on China for obtaining auto components [6]. The outbreak of the coronavirus not only affected the automobile industry but also had a significant impact on the automotive components and forging industries. China holds a

Funding: The authors received no specific funding for this work.

Competing interests: The authors have declared that no competing interests exist.
dominant position as the leading supplier of auto components in India, with 27\% of its exports. With the manufacturing facilities in China being temporarily shut down during the coronavirus crisis, numerous Indian automobile companies experienced substantial losses. Major companies like Tata Motors, Mahindra and Mahindra, and MG Motors in India have publicly acknowledged facing challenges in sourcing auto components from China, which has been severely affected by the virus [7]. Accordingly, Indian firms had to reconsider the structure of their SCs and how they should proceed in the future to predict, sense, and respond to future unexpected risks and crises in order to mitigate their impact.

Under these circumstances, companies need to build resilience that aids in "being alert to adapt to and respond to changes brought by a supply chain disruption effectively and efficiently [8]." The World Economic Forum [9] indicated that "more than 80\% of firms place a strong emphasis on resilience to disruptions." Supply chain resilience (SCR)- which refers to, "the adaptive capability of the SC to prepare for unexpected events, respond to disruption and recover from them by maintaining continuity of operations at the desired level of connectedness and control over structure and function" [10]- is an essential dynamic capability (DC) in facing disturbances [11]. Nonetheless, the massive volume of disruptions that firms encounter may render it impractical to rely solely on internal resources or capabilities in the long run.

The latest advancements in the area of information and communication technologies (ICT) have emphasized the importance of SC digital twins and digital information technologies in managing SC disruption risks [12, 13] and making the SC more resilient [14-16]. Moreover, previous research has demonstrated that ICT enhances supply chain integration (SCI) by effectively managing the increased volume and intricacies of information exchanged among various SC partners [e.g., 17]. In addition, there are expectations that Industry 4.0 technologies enabled by ICT will further enhance process integration, thereby strengthening SCR [14]. Among these technologies, blockchain stands out as a notable solution with significant potential for addressing the complexities of SCs [18-21]. Blockchain Technology (BCT) is "an organizational capability that integrates all the SC assets and resources, adding value to the activities such as product tracking, information sharing, and providing transparency in SC transactions" [17]. BCT reflects a firm's ability to incorporate an ICT background in manufacturing [22] that helps firms to achieve the efficient coordination and synchronization of efforts necessary to develop SCR. With the exception of anecdotal evidence, however, the previous literature has been muted on the role of BCT, which enables firms to share information in an entirely secure and transparent manner, hence improving SCR. It is anticipated that BCT will have a substantial effect on SC processes within the automotive industry context [17]. Furthermore, as far as we know, there is a lack of empirical evidence regarding the effect of BCT on SCR in the automobile industry, necessitating further investigation of the role of BCT adoption in SC.

Even though some prior studies have provided a rationale for investing in ICT to improve SCI [e.g., 23] and SCR [24, 25], other research has demonstrated that these investments have not effectively generated an effect on organizational resilience [26]. These discrepancies in the findings serve as an impetus for us to further explore the connection between digital technologies, which support SCI, and SCR. According to various studies [e.g., 17], SCI is an important factor in enhancing collaboration and partnerships within the SC. The adoption of BCT enables secure storage of all supply chain transactions, and easy access to all partners, enhancing the level of SCI [27]. Previous research [e.g., 28] has also recognized SCI as an important variable that mediates the association between independent and dependent variables in the field of operations management. BCT has the potential to augment SCI and thereby contribute to SCR. Therefore, the current study aims to explore whether SCI acts as a mediator in the BCT-SCR relationship.

By embracing the dynamic capabilities theory (DCT), this study visualizes BCT as a dynamic capability and examines its direct effect on SCR, as well as its indirect effect through SCI. However, evidence from other research reveals that firms interested in adopting BCT must take into account the external context effect on the motivation to use technology [29]. Thus, environmental dynamism (ED) is a critical situational parameter in DCT, implying that the variation of competitive edge gained by organizational capability exploitation is contingent on ED [30]. This perspective is exemplified by contingency theory (CT). However, Eckstein et al. [31] contend that conceptual and empirical research on SC capabilities has mainly disregarded the influence of pertinent contextual factors. Furthermore, Clohessy and Acton [32] assert that empirical research on BCT has mainly overlooked the effect of ED. Previous research demonstrates unequivocally that a tumultuous outer environment may either boost or degrade a firm's most vital capabilities [e.g., 33]. As a result, evaluating the effect of BCT under different levels of ED remains challenging, indicating a clear research gap. As such, we expect that the impact of BCT is highly likely to be amplified to improve SC performance in high-speed markets. Our argument is dependent on existing research that demonstrates how knowledge dissemination might result in increased variance in performance results in turbulent environments [34]. Hence, it can be contended that ED generates pressure on companies to utilize organizational knowledge as a guideline for decision-making. Consequently, there is a need for a more profound comprehension of the relationship between BCT, SCI, and SCR, as well as how ED moderates the BCT-SCI relationship.

This study makes a valuable contribution to the literature on operations management, information systems management and strategic management regarding the role of BCT in enhancing SCI to improve SCR under the influence of ED. Specifically, this study contributes in several ways. First, it examined the effect of BCT on SCR. This was a response to a call made by Sheel and Nath [35] to probe the impact of BCT adoption on critical SC performance parameters such as resilience. Second, it explored the mediating role of SCI between BCT and SCR. Third, it highlighted that ED can condition the extent to which BCT can enhance SCI and thus SCR. Finally, it examined the proposed model in the context of the automotive industry in India.

## 2 Theoretical background and hypotheses derivation

### 2.1 Theoretical basis

Relying on the DCT [e.g., 36] and the CT [e.g., 37], the conceptual model that illustrates the relationships among the key constructs of this study has been developed (see Fig 1).

![](https://cdn.mathpix.com/cropped/7fa57a38-50fb-4997-97d1-2e01f5de5315-03.jpg?height=400&width=984&top_left_y=1929&top_left_x=692)
Fig 1. Research model. Source: Authors' own work.
https://doi.org/10.1371/journal.pone.0295452.g001

According to DCT, a company seeking for long-term competitive advantage must either develop new resources and capabilities or deploy existing resources and capabilities to deal with emerging chances [38]. A DC is "the firm's ability to integrate, build, and reconfigure internal and external competences to address rapidly changing environments [36]." DCT is an expansion of the Resource-Based View (RBV) that elucidates how enterprises can attain a competitive edge in turbulent environments [18, 39]. There are numerous forms of capabilities, spanning from basic functional capabilities to dynamic high-level capabilities that are critical to an enterprise's strategic success [40]. DCs are critical for business survival, especially in quickly changing environments, such as those presently confronting manufacturing enterprises as a result of shifting market structures and technologies [41].

DCT has been widely adopted in the literature of operations management [42, 43]. The results demonstrate that DCs can be produced inside a focal firm in partnership with external partners within the SC, involving the reconfiguration of operating procedures to increase effectiveness. In SCM, this process entails developing the capabilities necessary to respond properly to changing environmental and market conditions [40]. Prior studies have identified SCR as a DC for anticipating and recovering from unavoidable risk events [10, 44]. SCR, as a DC, helps organizations to absorb the unfavorable consequences of a variety of risk sources [45]. As such, the ability of the SCR to absorb unforeseen interruptions and restore the SC to its former or improved case may result in competitive advantages [46]. Similarly, BCT capability is visualized in previous studies as a DC [e.g., 17]. As a result, we employ DCT as the theoretical foundation for the current study [36]. We theorize that BCT is a DC that can offer a competitive edge to a firm. Implementation of BCT can help firms to reduce the level of risk, as such the risk of information distortion across the SCs [47] by increasing transparency, accountability and visibility in SCs [48]. Therefore, we argue that BCT improves SCR via the intermediating role of SCI.

Although DCT is widely adopted, several researchers have argued that DCT is contextinsensitive [49, 50]. The impact of DCs on an enterprise's potential to attain better performance depends on the context in which the firm acts [36]. Consequently, we suggest that it is vital to analyze the circumstances under which capabilities are most valued. Contingency theory (CT) addresses this idea of context's importance in elucidating how a firm's inner and outer conditions result in disparate performance results [18, 51]. Thus, managers must perform an in-depth analysis of the organization's environment, taking into account internal firm features, and change practices accordingly [52]. CT has been identified as a critical theoretical lens for understanding the contextual conditions in which efficient operations management methods can be implemented [53], which contributes to the theoretical precision of research [54]. Hence, while considering CT, a variety of concepts of fit can be used and should be explicitly evaluated during the research process [53]. As a result of Schilke's [55] work, we adopt a contingency viewpoint operationalized through a fit moderation notion, which argues that the differential effects of BCT on SCI are dependent on the degree of the moderating variable (in this case ED). Since the objective of DCs is to equip organizations with the capacity to adapt to rapidly changing environments [56], we integrate DCT and CT to build the theoretical foundation of this study.

### 2.2 Blockchain technology and supply chain resilience

BCT is a beneficial tool to enhance resilience in contemporary SCs operating in a more dynamic business environment [57]. Previous research has revealed the positive influence of BCT on SC performance in general and on SCR in particular [e.g., 19, 58, 59]. According to Bayramova et al. [60], BCT has consequences for SCR in terms of visibility, information
sharing, risk management, and integration. The visibility metric is typically enhanced when BCT are adopted in the form of traceability systems [61], whereas information exchange and collaboration are typically enhanced when BCT are implemented as distributed ledger technology features [62, 63]. BCT is well-suited to service clients by allowing the tracking and tracing of orders from production to delivery and adjusting promptly [64]. BCT enables enhanced visibility of SCs and network-wide real-time data sharing. As a consequence, it can aid SCR strategies by minimizing the number of stakeholders impacted by a disruption [65]. In this context, Lambourdiere and Corbin [48] indicate that firms must incorporate BCT into the logistical processes of their SCs. By doing so, they can utilize this technology to develop capabilities within the SCs, which ultimately leads to the creation of more robust and resilient SCs. On the basis of the foregoing, it can be assumed that:

H1: BCT is significantly and positively associated with SCR.

### 2.3 Blockchain technology, supply chain integration, and supply chain resilience

BCT is digitally predisposed to integrate all SC processes among partners [35, 66], with many advantages such integration enables, such as "product traceability, settlement of transactions, process automation, and execution of smart contracts" [64]. According to Polim et al. [67], one of the key capabilities of BCT is the integration of information. SCI, which is enabled through BCT, is highly secured, as BCT prevents unauthorized access to the information stored on the ledger [17]. BCT facilitates the integration of supplier and customer information, resulting in exceedingly high levels of SCI [68]. BCT accelerates the execution of business activities while maintaining a high level of reliability and accuracy [69]. BCT allows records to be shared with SC partners [70, 71], hence resolving trust difficulties among partners [72]. Each member partner has access to the other's internal procedures. Kshetri [47] proposes incorporating BCT with the Internet of Things to determine the source of disturbances in SC and to effectively address crises. This incorporation enables the reduction of uncertainties and promotes enhanced process integration [73] and SC transparency [27]. Moreover, the incorporation of BCT in SCs leads to enhanced privacy, audibility, and increased operational efficiency [17]. Hence, we suppose that:

H2: BCT is significantly and positively associated with SCI.
Moreover, IT-based SCI allows sharing of data or information in real time [74]. Internal integration, as highlighted by Tiwari [75], facilitates the integration of all internal functions within an organization, resulting in improved communication and efficient decision-making processes [76]. By enabling the sharing of information, internal integration plays a crucial role [77], on the other side, operational integration between SC partners enhances SCR in response to disturbances [74]. Related to this, a study conducted in Taiwan by Liu and Lee [78] demonstrated that both internal integration and customer integration, which are forms of SCI, have a significant positive impact on SCR, particularly within third-party logistics providers. Furthermore, supplier integration can have a positive influence on enhancing SCR in terms of effectively dealing with uncertainties and responding promptly to disruptions in the SC [79]. Longstanding partnerships within the SC with suppliers who exhibit increasing levels of innovativeness can significantly impact SCR, as the pivot company has strong partnering relationships that enable it to quickly step back when faced with disruptions [80]. SCI improves SCR to build SC partnerships [2]. Firms' information technology can incorporate the system to enhance its response as a form of SCR [78]. Recent studies examining the impact of ICT-
enabled integration technologies like SC information systems on SC performance [e.g., 17], highlight SCI as a crucial mediating variable. Digital technologies-enabled SCI has a twofold effect on information processing demand and capacity. Additionally, digital technologiesenabled internal integration brings synergistic advantages, which improve the capability to manage the flow of information. This allows firms to swiftly prevent and respond to disruptions, thereby enhancing their resilience [81]. Based upon the preceding arguments, we suppose that:

H3: SCI is significantly and positively associated with SCR.
H4: SCI mediates the association of BCT with SCR.

### 2.4 The moderating role of environmental dynamism

ED is defined as "the volatility and unpredictability of the firm's external environment [55]." It is a critical factor in DCT [55], implying that the differential influences of DC on SC characteristics [82] and organizational performance [34] are dependent on the external environment's dynamism [38]. According to Eisenhardt and Martin [38], firms generally follow predictable and linear pathways in moderately dynamic marketplaces (characterized by defined market boundaries and stable industry structures). Therefore, effective DC in moderately dynamic environments is contingent upon making use of present knowledge. In comparison, changes in fast-moving markets (characterized by complex and ambiguous structures) are typically nonlinear and unpredictable [30]. In such dynamic environments, firms within SCs increasingly rely on collaboration and integration among stakeholders to adapt to changes and disruptions. Therefore, the role of new technological applications such as BCT in SCs becomes more important [57, 83]. Changes in the more complex and turbulent environment are driving firms to adopt BCT [84]. According to Meidute-Kavaliauskiene et al. [57], firms need to invest in BCT to respond swiftly to market changes and consumer expectations in today's volatile business environment. BCT is an important technology for firms to better control the flow of the SC. Furthermore, Liu and Li [85] asserted that BCT is well-suited to unpredictable and frequently changing environments and laws. In contrast, Orji et al. [86] claim that market dynamism has a negligible impact on BCT adoption in the freight logistics business and ranking fourth in the institutional context. Indeed, Meidute-Kavaliauskiene et al. [57] claim that the unforeseeable nature of ED's effect on organizational results gives companies with additional chances to leverage and explore BCT capabilities. Therefore, a new requirement to respond to market changes is to assess the utilize of digital technology in SC processes within the context of a dynamic market environment.

Environmental turbulence which entails uncertainty can have an effect on the adoption of BCT [87]. However, Wamba et al. [30] found that the effect of big data analytic on agility and adaptability did not differ under the influence of ED. In contrast, Liu et al.'s [88] study revealed that ED moderates the indirect influence of digital technologies such as BCT on environmental and economic performance via digital SC platforms. Thus, in order to achieve better performance, manufacturing organization must not only leverage on inner information processing abilities that are enabled by digital technologies, but also leverage the most advanced digital SC platforms to get additional information outside, particularly in a dynamic context. On the basis of the foregoing, we argue that ED can enhance the impact of BCT on SCI, hence affecting SCR. Accordingly, we propose the following:

H5: ED positively moderates the association of BCT with SCI.

## 3 Methodology

### 3.1 Sampling and data collection

In this study, the proposed model depicted in Fig 1 was evaluated through a survey-based methodology with data collected from Indian firms in the automotive industry. The firms were chosen from the "Society of Indian Automotive Manufacturers" and the "Automotive Components Manufacturers Association of India" databases. The questionnaire was designed and mailed to 300 managers from 100 firms. The authors took the help of a private market research firm to administer the questionnaire and collect the data. Participation in the survey was completely optional and restricted to only those respondents who had worked in the automotive industry for at least two years. This was done to ensure that some respondents had some level of acquaintance with the industry. In addition, only participants with prior knowledge of BCT and SCM concepts were asked to complete the survey. The target respondents were the supply chain/ logistics/production/manufacturing/digitalization and technology lead managers. To incentivize participants to fill out the questionnaire and boost the response rate, the questionnaire included a statement guaranteeing respondents' anonymity. Furthermore, regular e-mail reminders were sent out. The total number of respondents in this study was 300. Of this number, 148 were returned while 141 were complete and useable, representing a response rate of $47 \%$. This is a good percentage in comparison to those mentioned in earlier research [e.g., 89]. Following these procedures, data collection took three months (from midJune to mid-September 2022).

This study's participants varied in terms of gender (Male-84.4\% and Female-15.6\%); educational level (Secondary and below-13.48\%, Undergraduate-60.99\%, and Postgraduate-25.53\%); work experience (Less than 15 years-22.7\% and 15 years and above-77.3\%); age (20 to 29years3.55\%, 30 to 39years-14.9\%, 40 to 49years-52.48\%, and 50 years and above-29.07\%); and position (logistics manager-45.39\%, production/manufacturing manager-34.04\%, and digital technology/ICT manager-20.57\%).

### 3.2 Measures

For this study, the survey questionnaire instrument was used to collect the required data to examine the links in the proposed model. Initially, we conducted 6 personal interviews with academics and business professionals in order to ensure that the proposed survey questions are understandable and not ambiguous, vague, or difficult to reply [90]. The constructs and corresponding items employed for their measurement can be found in S1 Appendix.

To assure reliability and construct validity, all measurement items were obtained from existing literature and adapted to be appropriate to the context of this study. SCR was measured using 4 items derived from Al-Hakimi et al. [11]. For SCI, it was measured using 10 items derived from Kamble et al. [17]. While BCT was measured using 9 items derived from Kamble et al. [17] and Dubey et al. [18] and lastly ED was measured using 3 items derived from Wamba et al. [30].

### 3.3 Common method bias (CMB)

After the data collection phase, the initial step involved conducting a test for common method bias (CMB) before proceeding with further statistical analysis using the gathered data. CMB is "a common issue in statistical-based investigations when the data is collected from a single respondent from a firm, which may lead to an artificial increase in sample sizes and inflated estimates" [91]. To mitigate CMB, several steps were taken, including ensuring the clarity of measurement items, anonymizing participants, and selecting participants who possessed
knowledge of BCT and SC management [ibid]. Besides that, "Harman's one-factor" test was carried out as per the procedures of Podsakoff et al. [92], in order to verify the absence of CMB. According to Podsakoff et al. [92], a preliminary factor analysis is conducted for all questionnaire items such that if a single factor stands out in the analysis or if the first factor elucidates over 50\% of the variance, it indicates a substantial effect of error variance. While previous studies have indicated that Harman's method might not effectively identify CMB in comparison to other tests, some recent studies have confirmed that it is a very beneficial method [e.g., 93]. In our study, the factor identified accounted for 35\% of the total variance, indicating that CMB was not a concern for the collected data.

Furthermore, an alternative approach proposed by Fuller et al. [94] involved examining the collinearity variance inflation factor (VIF) using SmartPLS to assess the presence of CMB. The findings from this analysis indicated that the VIF values were below the recommended threshold of 3, as proposed by Fuller et al. [94]. Hence, the data does not raise concerns regarding the presence of CMB.

## 4 Data analysis and results

To analyze the relatively intricate model in this study, we utilized the PLS-SEM approach via SmartPLS 4 software, following the guidelines outlined by Ringle et al. [95]. The widespread utilization of PLS-SEM in administrative studies can be attributed to its numerous advantages [96]. Specifically, when working with smaller sample sizes [97] and when the research primarily focuses on prediction [93]; where it exhibits greater statistical power compared to "covariance-based SEM" (CB-SEM) when adopted with complex models with limited sample sizes [ibid].

Nevertheless, in recent times, some researchers have expressed concerns regarding the alleged inappropriate application of PLS-SEM, particularly concerning the arguments supporting its use in scenarios involving "small sample sizes, large model complexity, less restrictive distributional assumptions, and less restrictive utilization of formative measurement models" [93]. For instance, Evermann and Rönkkö [98] have raised a few questionable arguments, notably claiming that PLS-SEM is "a well-known bias estimator", often indicated to as the "PLS-SEM bias". However, simulation experiments have shown that the discrepancies between the estimations of PLS-SEM and CB-SEM are minimal [99]. Consequently, the widely examined PLS-SEM bias has little influence on the results of practical applications because of the asymptotic accuracy of estimates under consistent large-scale assumptions (e.g., a large sample size and a substantial number of indicators per latent variable) [100].

Furthermore, although PLS-SEM tends to produce biased estimates on average, these estimates exhibit lower variability when compared to the estimates resulting from CB-SEM [99]. This characteristic proves advantageous in research contexts where CB-SEM, based on maximum probability, often yields inflated standard errors [101] and violates certain assumptions, including "high model complexity, small sample size, non-normal data". The enhanced efficiency in parameter estimation is evidenced by the greater statistical power of PLS-SEM in comparison to CB-SEM. This aligns with the current analysis, as PLS-SEM is well-suited for examining relationships between multiple constructs simultaneously, even with a sample size of 141 cases. Overall, the PLS model encompasses two interdependent models: the "measurement model" and the "structural model".

### 4.1 Measurement model

For this study, the confirmatory composite analysis (CCA) approach, as outlined by Hair et al. [102], was employed to assess the measurement model. To ensure reliability, the values of

![](https://cdn.mathpix.com/cropped/7fa57a38-50fb-4997-97d1-2e01f5de5315-09.jpg?height=1008&width=1231&top_left_y=269&top_left_x=690)
Fig 2. Measurement model. Source: Authors' own work based on the statistical analysis (Smart PLS).
https://doi.org/10.1371/journal.pone.0295452.g002

"Cronbach's alpha ( $\alpha$ )" and "composite reliability" (CR) needed to surpass 0.70 , in accordance with Nunnally and Bernstein [103]. Furthermore, the construct validity was evaluated through the examination of "convergent validity" and "discriminant validity", following the guidelines provided by Hair et al. [102]. Convergent validity was validated when the value of "average variance extracted (AVE)" for each construct exceeded 0.50, as suggested by Hair et al. [104]. Additionally, the factor loadings for each item depicted in Fig 2 and Table 1 were required to exceed a minimum of 0.70 [ibid].

Moreover, the "Heterotrait-Monotrait (HTMT)" method, as outlined by Henseler et al. [105], was employed to verify discriminant validity. According to Al-Swidi et al. [93], the values within the HTMT matrix, especially between the constructs, must not surpass 0.90. In our study, the results demonstrated that the values did not surpass this threshold, as presented in Table 2.

From the results presented in Tables 1 and 2, it is evident that all requirements, including loadings, reliability, and validity, were met, which emphasizes the measurement model validity.

### 4.2 Structural model

Following the guidelines of the second step of the CCA approach, the structural model was evaluated in this study, as outlined by Hair et al. [102]. The significance of the paths in the model (as shown in Fig 3) was assessed using t-statistics, calculated through a bootstrapping technique [106].

Table 1. Loadings, reliability, and convergent validity.
| Constructs | Items code | Factor loading | CR (α) | AVE | Convergent validity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| BCT | BCT1 | 0.863 | 0.975 (0.969) | 0.802 | Yes |
|  | BCT2 | 0.874 |  |  |  |
|  | BCT3 | 0.914 |  |  |  |
|  | BCT4 | 0.860 |  |  |  |
|  | BCT5 | 0.909 |  |  |  |
|  | BCT6 | 0.930 |  |  |  |
|  | BCT7 | 0.932 |  |  |  |
|  | BCT8 | 0.864 |  |  |  |
|  | BCT9 | 0.908 |  |  |  |
| SCI | SCI1 | 0.828 | 0.949 <br> 0.949 (0.945) | 0.667 <br> 0.667 | Yes <br> Yes |
|  | SCI2 | 0.883 |  |  |  |
|  | SCI3 | 0.851 |  |  |  |
|  | SCI4 | 0.715 |  |  |  |
|  | SCI5 | 0.727 |  |  |  |
|  | SCI6 | 0.809 |  |  |  |
|  | SCI7 | 0.772 |  |  |  |
|  | SCI8 | 0.841 |  |  |  |
|  | SCI9 | 0.883 |  |  |  |
|  | SCI10 | 0.842 |  |  |  |
| ED | ED1 | 0.814 | 0.782 (0.775) | 0.688 | Yes |
|  | ED2 | 0.860 |  |  |  |
|  | ED3 | 0.814 |  |  |  |
| SCR | SCR1 | 0.941 | 0.968 (0.965) | 0.905 | Yes |
|  | SCR2 | 0.952 |  |  |  |
|  | SCR3 | 0.958 |  |  |  |
|  | SCR4 | 0.955 |  |  |  |


https://doi.org/10.1371/journal.pone.0295452.t001

Table 3 shows the results of the hypotheses testing. The results demonstrate that paths $(\mathrm{BCT} \rightarrow \mathrm{SCI})(\beta=0.232, \mathrm{p}<0.01)$ and $(\mathrm{SCI} \rightarrow \mathrm{SCR})(\beta=0.334, \mathrm{p}<0.01)$ were positive and significant, supporting H2 and H3. In addition, the path $(\mathrm{BCT} \rightarrow \mathrm{SCR})(\beta=0.040, \mathrm{p}>0.05)$ was insignificant when there was no putative mediator (SCI); however, this effect of BCT on SCR became significant $(\beta=0.077, \mathrm{p}<0.05)$ when the putative median was included. Therefore, hypothesis H1 is not supported.

Along with the linear paths of our proposed model, we investigated the moderating effect of ED on the path linking BCT and SCI, as the results revealed that ED positively and significantly moderates the path $(\mathrm{BCT} \rightarrow \mathrm{SCI})(\beta=0.282, \mathrm{p}<0.01)$. Hence, hypothesis H5 is supported (see Fig 4). The outcome reveals that a strong correlation exists between high ED and increased levels of SCI, particularly when companies implement a high degree of BCT.

Table 2. Discriminant validity.
| Constructs | BCT | SCI | ED | SCR |
| :--- | :--- | :--- | :--- | :--- |
| BCT |  |  |  |  |
| SCI | 0.300 |  |  |  |
| ED | 0.190 | 0.428 |  |  |
| SCR | 0.146 | 0.361 | 0.105 |  |


https://doi.org/10.1371/journal.pone.0295452.t002

![](https://cdn.mathpix.com/cropped/7fa57a38-50fb-4997-97d1-2e01f5de5315-11.jpg?height=1001&width=1229&top_left_y=271&top_left_x=692)
Fig 3. Structural model. Source: Authors' own work based on the statistical analysis (Smart PLS).

https://doi.org/10.1371/journal.pone.0295452.g003

Moreover, in accordance with the guidelines presented by Sarstedt et al. [107], the mediating role of SCI between BCT and SCR was investigated. The findings, which are outlined in Table 4, provide confirmation that SCI acts as a full mediator in the BCT-SCR relationship. Thus, H4 is supported.

As a next step, the explanatory power of the study model was evaluated by calculating the explained variance $\left(\mathrm{R}^{2}\right)$ of the endogenous constructs, where the $\mathrm{R}^{2}$ values in the model were as follows: SCI (0.316) and SCR (0.121), as demonstrated in Table 5. To assess the results, Chin's guidelines for prediction "0.10 = weak, $0.33=$ moderate, $0.67=$ large" were utilized [108].

Additionally, Cohen's $\mathrm{f}^{2}$ guidelines were employed to evaluate the effect size of each predictor [109], where the $\mathrm{f}^{2}$ values of $0.35,0.15$, and 0.02 are classified as 'large', 'medium', and 'small', respectively. Accordingly, the effect size of BCT on SCI was 0.076 ; BCT on SCR was 0.002; ED on SCI was 0.242; and SCI on SCR was 0.114 (see Table 5). Moreover, the predictive capability of the model was assessed through Stone-Geisser $\left(\mathrm{Q}^{2}\right)$. The $\mathrm{Q}^{2}$ values for the

Table 3. Direct and moderation effect.
| Direct paths | $\beta$ | t value | p value | Decision |
| :--- | :--- | :--- | :--- | :--- |
| BCT→SCR | 0.040 | 0.457 | 0.648 | Not supported |
| BCT→SCI | 0.232 | 3.142 | 0.002 | Supported |
| SCI→SCR | 0.334 | 3.751 | 0.000 | Supported |
| Moderation | $\beta$ | t value | p value | Decision |
| ED*BCT→SCI | 0.282 | 3.947 | 0.000 | Supported |


![](https://cdn.mathpix.com/cropped/7fa57a38-50fb-4997-97d1-2e01f5de5315-12.jpg?height=539&width=838&top_left_y=269&top_left_x=692)
Fig 4. Moderation effect of ED on BCT and SCI. Source: Authors' own work based on the statistical analysis (Smart PLS).

https://doi.org/10.1371/journal.pone.0295452.g004
endogenous constructs, SCI and SCR, were 0.264 and 0.040 , respectively. These values, being above zero, indicate satisfactory predictive relevance [106].

As a last evaluation of the structural model's predictive abilities, the PLSpredict procedure was executed to assess the prediction errors, following the methodology outlined by Manley et al. [110]. The evaluation process involved the calculation of $\mathrm{Q}^{2}$ and a comparison of the prediction errors between PLS and LM. Table 6 presents the $Q^{2}$ values obtained by comparing the prediction errors of the PLS results with those of the mean predictions. All $\mathrm{Q}^{2}$ values were found to be higher than zero, which indicates that the prediction error associated with the PLS results was less than the prediction error resulting from depending solely on mean values. Moreover, the differences between LM and PLS in terms of indicators such as "mean absolute error (MAE)" and "root-mean-square error (RMSE)" were relatively minor. As per the recommendations provided by Hair et al. [102], "the model has medium predictive power when only a few indicators in the PLS analysis exhibit larger prediction errors compared to the LM criterion". Therefore, the model's predictive validity was verified.

## 5 Discussion

Guided by DCT and CT, we explored how and when BCT adoption improves SCR. According to the results, BCT does not directly affect SCR. This result is in line with the previous studies [e.g., 111], which revealed that digital technologies (In this case, BCT) had an insignificant effect on SCR in the presence of putative mediators. On the contrary, it contradicts the findings of Min [19], which have previously demonstrated a positive effect of BCT on SCR. The results also indicate that BCT positively affects SCI. This is in line with the results of prior research [e.g., 17]. On the other hand, our results reveal that SCI positively affects SCR, which is similar to the results of Siagian et al. [74] and Tarigan et al.'s [79] studies.

Table 4. Indirect effect.
| Mediation paths | Indirect path |  |  | Direct path |  |  | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|  | $\boldsymbol{\beta}$ | t value | p value | $\boldsymbol{\beta}$ | t value | p value |  |
| BCT →SCI →SCR | 0.077 | 2.445 | 0.015 | 0.040 | 0.457 | 0.648 | Fully mediation |


https://doi.org/10.1371/journal.pone.0295452.t004

Table 5. $\mathrm{R}^{2}$, prediction, and effect size.
| Constructs | $\mathbf{R}^{\mathbf{2}}$ | $\mathbf{Q}^{\mathbf{2}}$ | $\mathbf{f}^{\mathbf{2}}$ in relation to |  |
| :--- | :--- | :--- | :--- | :--- |
|  |  |  | SCI | SCR |
| BCT |  |  | 0.076 | 0.002 |
| ED |  |  | 0.242 |  |
| SCI | 0.316 | 0.264 |  | 0.114 |
| SCR | 0.121 | 0.040 |  |  |


https://doi.org/10.1371/journal.pone.0295452.t005

As expected, the findings also show that SCI mediates between BCT and SCR, where BCT indirectly affects SCR through the full mediation of SCI. Importantly, the results show that the association between BCT and SCI will be stronger under a high level of ED.

As a result, this study contains some noteworthy contributions to theory and evidence for managers, as detailed in the following sections.

### 5.1 Theoretical implications

The theoretical contribution of the current study is many folds. First, based on DCT and CT, this study contributes to theoretical arguments surrounding DCs (in this case, BCT and SCR) mediated by SCI and under the conditional impacts of ED. The current study can be considered an attempt to incorporate literature from three areas: operations management, information systems management, and strategic management. While Dubey et al. [112] and Wamba et al. [30] have attempted to fill the divide between operations management and information systems literature in the past, these studies have relied on DCT or information processing theory, or the incorporation of institutional theory and RBV. Second, the results of the study pertinent to the role of BCT for SCR complement the previous studies on other SCR enablers such as IT [113], as technical sources for SCR. In this regard, a firm's capability to integrate a BCT into its overall operating structure is as a barometer of its capability to develop SCR. Furthermore, we respond to a call made by Ying et al. [114] to enrich the present status of exploratory research on BCT by providing more empirical evidence. In fact, the majority of the

Table 6. PLSpredict assessment.
| Indicators | $\mathbf{Q}^{\mathbf{2}}$ | PLS |  | LM |  |
| :--- | :--- | :--- | :--- | :--- | :--- |
|  |  | RMSE | MAE | RMSE | MAE |
| SCI1 | 0.067 | 0.644 | 0.508 | 0.632 | 0.503 |
| SCI2 | 0.086 | 0.707 | 0.526 | 0.684 | 0.518 |
| SCI3 | 0.080 | 0.695 | 0.531 | 0.727 | 0.559 |
| SCI4 | 0.258 | 0.533 | 0.369 | 0.525 | 0.390 |
| SCI5 | 0.270 | 0.609 | 0.421 | 0.603 | 0.453 |
| SCI6 | 0.300 | 0.548 | 0.434 | 0.607 | 0.473 |
| SCI7 | 0.233 | 0.580 | 0.453 | 0.662 | 0.519 |
| SCI8 | 0.067 | 0.635 | 0.503 | 0.630 | 0.504 |
| SCI9 | 0.072 | 0.723 | 0.544 | 0.730 | 0.553 |
| SCI10 | 0.061 | 0.676 | 0.529 | 0.720 | 0.571 |
| SCR1 | 0.030 | 0.574 | 0.524 | 0.618 | 0.554 |
| SCR2 | 0.041 | 0.604 | 0.541 | 0.661 | 0.569 |
| SCR3 | 0.024 | 0.575 | 0.525 | 0.617 | 0.552 |
| SCR4 | 0.048 | 0.592 | 0.536 | 0.650 | 0.568 |


https://doi.org/10.1371/journal.pone.0295452.t006
existing literature on BCT is a review of the literature [e.g., 115, 116] and is conceptual in nature [e.g., 117, 118]. While a few researchers have made efforts to study BCT empirically, their studies were qualitative in nature [87], relatively narrow in scope [114], and based on the Technology Acceptance Model [68] or Unified theoretical frameworks of the Acceptance Model [119]. Thus, by combining the theoretical lens of the DCT and CT frameworks with empirical evidence from Indian automotive manufacturing firms, this study contributes to the expanding body of knowledge on BCT and diversify the literature on operations management and information technology. Third, this study examines the mediating role of SCI between BCT and SCR. In comparison to the present research on the importance of IT, our results propose that the relationship between BCT and SCR is more likely to be complex, not narrowscoped. In doing so, we add to the work of Pattanayak et al. [120] by proposing the mechanism through which BCT improves SCR. Fourth, this study establishes that ED plays a crucial role in the link between BCT and SCI. Thus, our study contributes to bridging the critical research gap concerning the effect of BCT on SCI and under what conditions do BCT contribute to the enhancement of DCs (SCP), which are probably among the most urgent research problems in the domain of operations and SCM. The inclusion of ED into the image develops a conditioned vision of the function that BCT plays in SCR indirectly via SCI. By incorporating existent arguments on DCs under varied levels of ED, we argue that DCT [36] is insufficient for dealing with highly dynamic and uncertain environments. As a result, our results imply that the interaction between BCT, SCI, and SCR may be more complicated than a simpler linear relationship.

### 5.2 Managerial implications

The study's findings have valuable managerial implications for firms seeking to develop SCR and attain high performance in turbulent environments. First, an in-depth analysis of the findings shows that firms should adopt BCT to minimize the influences of SC disruptions and enhance SCR as a whole. The study's findings imply that managers should carefully assess the SC capabilities (SCR) for sensing dynamic changes in the inner and outer environment, which may aid in shaping chances and mitigating disturbances. In general, managers realize the issues surrounding SC disruptions and the critical role of SCR [121]. Nevertheless, their knowledge of the role of BCT in developing SCR may be less complete. Furthermore, the current study emphasizes and reminds managers of the crucial role of resilience in managing SC disruption as it occurred in the unique period of the COVID-19 pandemic and in the event of future epidemic outbreaks or crises. This highlights the critical and pressing need for enterprises, as well as governments, to invest in developing fundamental capabilities of resilient SCs in order to improve performance during such crises. Although SCR is a relatively new term that is not widely discussed in some developing countries, many firms in India for example are beginning to realize that improving SCR is critical to their global competitiveness, which requires greater knowledge about risk mitigation strategies [122]. Second, our findings indicate that BCT is a capability that does not impact a firm's performance outcomes [e.g., 123], but is also utilized for the development of other capabilities, such as SCR. However, this effect is indirect, as our findings inform practice by indicating the sequence in which capabilities should be developed and implemented (BCT→SCI→SCR). Pursuing to embrace the BCTenabled DCs in SCs aids in developing a firm's response to disturbances in the form of SCR, which eventually boosts SC performance [122]. Our findings indicate that adopting BCT enhances SCI, where it dramatically minimizes the number of partners influenced by perturbation, the cost of the disruption, and the time required for the network to recover. Adopting BCT can be a fruitful solution for enhancing SCR, however, the costs and time it takes to set
up and run must be taken into account. In this regard, managers should adopt BCT as a solution within the context of stated joint risk management systems within the SC, which should include a joint risk strategy. However, it is necessary to upgrade and connect the underlying risk management procedures before implementing BCT solutions. Furthermore, managers interested in adopting and developing BCT-based IT solutions for the SC should begin lobbying SC partners to design a regulatory framework for BCT. Without a regulatory framework, the technology will remain extremely dangerous to adopt. At the moment, in a country like India, there is no specific legal structure in place to address BCT [35]. India has begun to investigate BCT implementation in the SC [68], and India now has an opportunity to improve its global competitiveness [124]. However, given the additional transparency brought about by BCT adoption, corporations are recommended to conduct a thorough study to ascertain partners' reactions to a fully transparent SC that allows for close monitoring of customers and other parties, including rivals [117]. Third, our work demonstrates the importance of DCs in developing countries. Numerous earlier studies have established that DCs are only useful in a fast-paced context. Our findings indicate that DCs are important in both developed and developing countries. This is because dynamism encompasses more than competition and rapid invention. Another factor to consider is susceptibility to interruptions. This is a more prevalent or serious issue in developing countries. As a result, enterprises in developing nations must invest in creating DCs if they seek to survive in the face of continual disturbances. While some routines emerge by chance, others require managers to have patience and forethought in determining when and how to construct DCs, as well as how to explore and use DCs concurrently to achieve a competitive edge.

### 5.3 Limitations and future research

Like other studies, this study has some limitations. First, while the DCT has garnered considerable attention, we contend that it suffers from context insensitivity, as stated by Ling-Yee [49]. We explicate context sensitivity to mean that DCT is incapable of identifying the circumstances in which DCs are most helpful [55, 112]. Although we tried to deal with this limitation of the firm's DCT by incorporating DCT with CT, when examining the moderating role of ED, we believe that further research can be conducted to determine the optimal conditions under which BCT can achieve SCI in order to improve SCR. Second, as with any survey-based study, this one has limitations, such as CMB or endogeneity [125]. As a result, we used statistical approaches to detect CMB. However, this study cannot rule out the potential of CMB. Future study may employ longitudinal or multiple informant data to examine the potential links in the research model. Third, the results of this study depend on managers' perspectives in the context of the automotive industry, so they are not generalizable in the context of services that also suffer from disruptions in SCs. Finally, we examined ED as a proxy for market dynamism in our study. Considering the significance of this concept in the context of DCs, additional sources of dynamism may be explored, including uncertainty, competitiveness, and technology.

## Supporting information

S1 Appendix. Questionnaire items.
(DOCX)
S1 Dataset.
(RAR)

## Author Contributions

Conceptualization: Abdullah Kaid Al-Swidi, Mohammed A. Al-Hakimi.
Data curation: Mohammed A. Al-Hakimi.
Formal analysis: Abdullah Kaid Al-Swidi.
Investigation: Abdullah Kaid Al-Swidi, Hussam Al Halbusi.
Methodology: Abdullah Kaid Al-Swidi, Mohammed A. Al-Hakimi.
Resources: Abdullah Kaid Al-Swidi, Hussam Al Halbusi, Jaithen Abdullah Al Harbi.
Supervision: Abdullah Kaid Al-Swidi, Jaithen Abdullah Al Harbi.
Validation: Abdullah Kaid Al-Swidi, Mohammed A. Al-Hakimi, Hussam Al Halbusi.
Visualization: Mohammed A. Al-Hakimi.
Writing - original draft: Abdullah Kaid Al-Swidi, Mohammed A. Al-Hakimi.
Writing - review \& editing: Abdullah Kaid Al-Swidi, Hussam Al Halbusi, Jaithen Abdullah Al Harbi, Hamood Mohammed Al-Hattami.

## References

1. Gölgeci I., \& Kuivalainen O. (2020). Does social capital matter for supply chain resilience? The role of absorptive capacity and marketing-supply chain management alignment. Industrial Marketing Management, 84, 63-74. https://doi.org/10.1016/j.indmarman.2019.05.006
2. Pettit T. J., Croxton K. L., \& Fiksel J. (2013). Ensuring supply chain resilience: development and implementation of an assessment tool. Journal of business logistics, 34(1), 46-76. https://doi.org/10.1111/jbl. 12009
3. Alexander A., Blome C., Schleper M.C. and Roscoe S. (2022). Managing the "new normal": the future of operations and supply chain management in unprecedented times. International Journal of Operations \& Production Management, 1-16. https://doi.org/10.1108/IJOPM-06-2022-0367
4. Ozdemir D., Sharma M., Dhir A., \& Daim T. (2022). Supply chain resilience during the COVID-19 pandemic. Technology in Society, 68, 1-10. https://doi.org/10.1016/j.techsoc.2021.101847 PMID: 35075312
5. Aneja R., \& Ahuja V. (2021). An assessment of socioeconomic impact of COVID-19 pandemic in India. Journal of Public Affairs, 21(2), 1-7. https://doi.org/10.1002/pa. 2266 PMID: 33173441
6. Muhammad M. S., Kerbache L., \& Elomri A. (2022). Potential of additive manufacturing for upstream automotive supply chains. Supply Chain Forum: An International Journal, 23(1), 1-19. https://doi.org/10.1080/16258312.2021.1973872
7. Rakshit B., \& Basistha D. (2020). Can India stay immune enough to combat COVID-19 pandemic? An economic query. Journal of Public Affairs, 20(4), 1-7. https://doi.org/10.1002/pa. 2157 PMID: 32837315
8. Ambulkar S., Blackhurst J., \& Grawe S. (2015). Firm's resilience to supply chain disruptions: Scale development and empirical examination. Journal of operations management, 33, 111-122. https://doi. org/10.1016/j.jom.2014.11.002
9. World Economic Forum (2013), Building Resilience in Supply Chains, World Economic Forum, Davos. 1-44. May 10, 2022 from: https://www3.weforum.org/docs/WEF_RRN_MO_BuildingResilienceSupplyChains_Report_2013.pdf.
10. Ponomarov S. Y., \& Holcomb M. C. (2009). Understanding the concept of supply chain resilience. The international journal of logistics management, 20(1), 124-143. https://doi.org/10.1108/09574090910954873
11. Al-Hakimi M. A., Saleh M. H., \& Borade D. B. (2021). Entrepreneurial orientation and supply chain resilience of manufacturing SMEs in Yemen: the mediating effects of absorptive capacity and innovation. Heliyon, 7(10), 1-12. https://doi.org/10.1016/j.heliyon.2021.e08145 PMID: 34660936
12. Ivanov D., \& Dolgui A. (2020). Viability of intertwined supply networks: extending the supply chain resilience angles towards survivability. A position paper motivated by COVID-19 outbreak. International Journal of Production Research, 58(10), 2904-2915. https://doi.org/10.1080/00207543.2020.1750727

13. Yeniyurt S., Wu F., Kim D., \& Cavusgil S. T. (2019). Information technology resources, innovativeness, and supply chain capabilities as drivers of business performance: A retrospective and future research directions. Industrial Marketing Management, 79, 46-52. https://doi.org/10.1016/j.indmarman.2019. 03.008
14. Frederico G.F., Kumar V., Garza-Reyes J.A., Kumar A. and Agrawal R. (2021). Impact of I4.0 technologies and their interoperability on performance: future pathways for supply chain resilience post-COVID-19. The International Journal of Logistics Management, 1-30. https://doi.org/10.1108/IJLM-03-2021-0181
15. Gupta H., Yadav A. K., Kusi-Sarpong S., Khan S. A., \& Sharma S. C. (2022). Strategies to overcome barriers to innovative digitalisation technologies for supply chain logistics resilience during pandemic. Technology in Society, 69, 1-12. https://doi.org/10.1016/j.techsoc.2022.101970
16. Tortorella G., Fogliatto F.S., Gao S. and Chan T.-K. (2022). Contributions of Industry 4.0 to supply chain resilience. The International Journal of Logistics Management, 33(2), 547-566. https://doi.org/10.1108/IJLM-12-2020-0494
17. Kamble S. S., Gunasekaran A., Subramanian N., Ghadge A., Belhadi A., \& Venkatesh M. (2021). Blockchain technology's impact on supply chain integration and sustainable supply chain performance: Evidence from the automotive industry. Annals of Operations Research, 1-26. https://doi.org/10.1007/s10479-021-04129-6
18. Dubey R., Gunasekaran A., Bryde D. J., Dwivedi Y. K., \& Papadopoulos T. (2020). Blockchain technology for enhancing swift-trust, collaboration and resilience within a humanitarian supply chain setting. International Journal of Production Research, 58(11), 3381-3398. https://doi.org/10.1080/00207543.2020.1722860
19. Min H. (2019). Blockchain technology for enhancing supply chain resilience. Business Horizons, 62 (1), 35-45. https://doi.org/10.1016/j.bushor.2018.08.012
20. Rane S.B. and Narvel Y.A.M. (2021). Re-designing the business organization using disruptive innovations based on blockchain-IoT integrated architecture for improving agility in future Industry 4.0. Benchmarking: An International Journal, 28(5), 1883-1908. https://doi.org/10.1108/BIJ-12-2018-0445
21. Kouhizadeh M., Saberi S., \& Sarkis J. (2021). Blockchain technology and the sustainable supply chain: Theoretically exploring adoption barriers. International Journal of Production Economics, 231, 1-79. https://doi.org/10.1016/j.ijpe.2020.107831
22. De Mattos C. A., \& Laurindo F. J. B. (2017). Information technology adoption and assimilation: Focus on the suppliers portal. Computers in industry, 85, 48-57. https://doi.org/10.1016/j.compind.2016.12.009
23. Vanpoucke E., Vereecke A., \& Muylle S. (2017). Leveraging the impact of supply chain integration through information technology. International Journal of Operations \& Production Management, 37 (4), 510-530. https://doi.org/10.1108/IJOPM-07-2015-0441
24. Balakrishnan A. S., \& Ramanathan U. (2021). The role of digital technologies in supply chain resilience for emerging markets' automotive sector. Supply Chain Management. An International Journal, 26(6), 654-671. https://doi.org/10.1108/SCM-07-2020-0342
25. Zhao N., Hong J., \& Lau K. H. (2023). Impact of supply chain digitalization on supply chain resilience and performance: A multi-mediation model. International Journal of Production Economics, 259, 1-19. https://doi.org/10.1016/j.ijpe.2023.108817 PMID: 36852136
26. Bürgel T. R., Hiebl M. R., \& Pielsticker D. I. (2023). Digitalization and entrepreneurial firms' resilience to pandemic crises: Evidence from COVID-19 and the German Mittelstand. Technological Forecasting and Social Change, 186, 1-18. https://doi.org/10.1016/j.techfore.2022.122135 PMID: 36339291
27. Biswas, K., Muthukkumarasamy, V., \& Tan, W. L. (2017). Blockchain based wine supply chain traceability system. In Future Technologies Conference (FTC), Vancouver, Canada 29-30 Nov. 2017 (pp. 56-62). The Science and Information Organization. UK. https://saiconference.com/Conferences/FTC2017.
28. Flynn B. B., Huo B., \& Zhao X. (2010). The impact of supply chain integration on performance: A contingency and configuration approach. Journal of operations management, 28(1), 58-71. https://doi. org/10.1016/j.jom.2009.06.001
29. Chowdhury S., Rodriguez-Espindola O., Dey P., \& Budhwar P. (2022). Blockchain technology adoption for managing risks in operations and supply chain management: evidence from the UK. Annals of Operations Research, 1-36. https://doi.org/10.1007/s10479-021-04487-1 PMID: 35095153
30. Wamba S. F., Dubey R., Gunasekaran A., \& Akter S. (2020). The performance effects of big data analytics and supply chain ambidexterity: The moderating effect of environmental dynamism. International Journal of Production Economics, 222, 1-51. https://doi.org/10.1016/j.ijpe.2019.09.019

31. Eckstein D., Goellner M., Blome C., \& Henke M. (2015). The performance impact of supply chain agility and supply chain adaptability: the moderating effect of product complexity. International Journal of Production Research, 53(10), 3028-3046. https://doi.org/10.1080/00207543.2014.970707
32. Clohessy T. and Acton T. (2019). Investigating the influence of organizational factors on blockchain adoption: An innovation theory perspective. Industrial Management \& Data Systems, 119(7), 1457-1491. https://doi.org/10.1108/IMDS-08-2018-0365
33. Afuah A. (2001). Dynamic boundaries of the firm: are firms better off being vertically integrated in the face of a technological change?. Academy of Management journal, 44(6), 1211-1228. https://doi.org/10.5465/3069397
34. Chen D. Q., Preston D. S., \& Swink M. (2015). How the use of big data analytics affects value creation in supply chain management. Journal of management information systems, 32(4), 4-39. https://doi. org/10.1080/07421222.2015.1138364
35. Sheel A. and Nath V. (2019). Effect of blockchain technology adoption on supply chain adaptability, agility, alignment and performance. Management Research Review, 42(12), 1353-1374. https://doi. org/10.1108/MRR-12-2018-0490
36. Teece D. J., Pisano G., \& Shuen A. (1997). Dynamic capabilities and strategic management. Strategic management journal, 18(7), 509-533. https://doi.org/10.1002/(SICI)1097-0266(199708)18:7<509::AID-SMJ882>3.0.CO;2-Z
37. Lawrence P. R., \& Lorsch J. W. (1967). Differentiation and integration in complex organizations. Administrative science quarterly, 12(1), 1-47. https://doi.org/10.2307/2391211
38. Eisenhardt K. M., \& Martin J. A. (2000). Dynamic capabilities: what are they?. Strategic management journal, 21(10-11), 1105-1121. https://doi.org/10.1002/1097-0266(200010/11)21:10/11<1105::AID-SMJ133>3.0.CO;2-E
39. Teece D. J. (2014). The foundations of enterprise performance: Dynamic and ordinary capabilities in an (economic) theory of firms. Academy of management perspectives, 28(4), 328-352. https://doi. org/10.5465/amp.2013.0116
40. Eslami M. H., Jafari H., Achtenhagen L., Carlbäck J., \& Wong A. (2021). Financial performance and supply chain dynamic capabilities: the Moderating Role of Industry 4.0 technologies. International Journal of Production Research, 1-18. https://doi.org/10.1080/00207543.2021.1966850
41. McAdam R., Bititci U., \& Galbraith B. (2017). Technology alignment and business strategy: A performance measurement and dynamic capability perspective. International Journal of Production Research, 55(23), 7168-7186. https://doi.org/10.1080/00207543.2017.1351633
42. Al-Hakimi M.A., Borade D.B. and Saleh M.H. (2022). The mediating role of innovation between entrepreneurial orientation and supply chain resilience. Asia-Pacific Journal of Business Administration, 14(4), 592-616. https://doi.org/10.1108/APJBA-10-2020-0376
43. Goaill M. M., \& Al-Hakimi M. A. (2021). Does absorptive capacity moderate the relationship between entrepreneurial orientation and supply chain resilience?. Cogent Business \& Management, 8(1), 1-20. https://doi.org/10.1080/23311975.2021.1962487
44. Brusset X., \& Teller C. (2017). Supply chain capabilities, risks, and resilience. International Journal of Production Economics, 184, 59-68. https://doi.org/10.1016/j.ijpe.2016.09.008
45. Teece D. J. (2007). Explicating dynamic capabilities: the nature and microfoundations of (sustainable) enterprise performance. Strategic management journal, 28(13), 1319-1350. https://doi.org/10.1002/smj. 640
46. Kamalahmadi M., \& Parast M. M. (2016). A review of the literature on the principles of enterprise and supply chain resilience: Major findings and directions for future research. International journal of production economics, 171, 116-133. https://doi.org/10.1016/j.ijpe.2015.10.023
47. Kshetri N. (2018). 1 Blockchain's roles in meeting key supply chain management objectives. International Journal of information management, 39, 80-89. https://doi.org/10.1016/j.ijinfomgt.2017.12. 005
48. Lambourdiere E. and Corbin E. (2020). Blockchain and maritime supply-chain performance: dynamic capabilities perspective. Worldwide Hospitality and Tourism Themes, 12(1), 24-34. https://doi.org/10. 1108/WHATT-10-2019-0069
49. Ling-Yee L. (2007). Marketing resources and performance of exhibitor firms in trade shows: A contingent resource perspective. Industrial Marketing Management, 36(3), 360-370. https://doi.org/10. 1016/j.indmarman.2005.11.001
50. Gunasekaran A., Papadopoulos T., Dubey R., Wamba S. F., Childe S. J., Hazen B., et al. (2017). Big data and predictive analytics for supply chain and organizational performance. Journal of Business Research, 70, 308-317. https://doi.org/10.1016/j.jbusres.2016.08.004

51. Iyer K. N., Germain R., \& Claycomb C. (2009). B2B e-commerce supply chain integration and performance: A contingency fit perspective on the role of environment. Information \& Management, 46(6), 313-322. https://doi.org/10.1016/j.im.2009.06.002
52. Volberda H. W., Van Der Weerdt N., Verwaal E., Stienstra M., \& Verdu A. J. (2012). Contingency fit, institutional fit, and firm performance: A metafit approach to organization-environment relationships. Organization Science, 23(4), 1040-1054. https://doi.org/10.1287/orsc.1110.0687
53. Sousa R., \& Voss C. A. (2008). Contingency research in operations management practices. Journal of Operations Management, 26(6), 697-713. https://doi.org/10.1016/j.jom.2008.06.001
54. Boyd B. K., Takacs Haynes K., Hitt M. A., Bergh D. D., \& Ketchen D. J. Jr (2012). Contingency hypotheses in strategic management research: Use, disuse, or misuse?. Journal of management, 38(1), 278-313. https://doi.org/10.1177/0149206311418662
55. Schilke O. (2014). On the contingent value of dynamic capabilities for competitive advantage: The nonlinear moderating effect of environmental dynamism. Strategic management journal, 35(2), 179-203. https://doi.org/10.1002/smj. 2099
56. Coreynen W., Matthyssens P., Vanderstraeten J., \& van Witteloostuijn A. (2020). Unravelling the internal and external drivers of digital servitization: A dynamic capabilities and contingency perspective on firm strategy. Industrial Marketing Management, 89, 265-277. https://doi.org/10.1016/j.indmarman. 2020.02.014
57. Meidute-Kavaliauskiene I., Yıldız B., Çiğdem Ş., \& Činčikaitė R. (2021). An integrated impact of blockchain on supply chain applications. Logistics, 5(2), 1-18. https://doi.org/10.3390/logistics5020033
58. Ivanov D., Dolgui A., \& Sokolov B. (2019). The impact of digital technology and Industry 4.0 on the ripple effect and supply chain risk analytics. International Journal of Production Research, 57(3), 829-846. https://doi.org/10.1080/00207543.2018.1488086
59. Paul S., Adhikari A., \& Bose I. (2022). White knight in dark days? Supply chain finance firms, blockchain, and the COVID-19 pandemic. Information \& Management, 59(6), 103661. https://doi.org/10. 1016/j.im.2022.103661
60. Bayramova A., Edwards D. J., \& Roberts C. (2021). The role of blockchain technology in augmenting supply chain resilience to cybercrime. Buildings, 11(7), 1-19. https://doi.org/10.3390/ buildings11070283
61. Czachorowski K., Solesvik M., \& Kondratenko Y. (2019). The application of blockchain technology in the maritime industry. In Green IT engineering: Social, business and industrial applications (pp. 561-577). Springer, Cham.
62. Gonczol P., Katsikouli P., Herskind L., \& Dragoni N. (2020). Blockchain implementations and use cases for supply chains-a survey. IEEE Access, 8, 11856-11871. https://doi.org/10.1109/ACCESS. 2020.2964880
63. Toufaily E., Zalan T., \& Dhaou S. B. (2021). A framework of blockchain technology adoption: An investigation of challenges and expected value. Information \& Management, 58(3), 1-17. https://doi.org/10. 1016/j.im.2021.103444
64. Chang S. E., Chen Y. C., \& Lu M. F. (2019). Supply chain re-engineering using blockchain technology: A case of smart contract based tracking process. Technological Forecasting and Social Change, 144, 1-11. https://doi.org/10.1016/j.techfore.2019.03.015
65. Lohmer J., Bugert N., \& Lasch R. (2020). Analysis of resilience strategies and ripple effect in blockchain-coordinated supply chains: An agent-based simulation study. International Journal of Production Economics, 228, 1-13. https://doi.org/10.1016/j.ijpe.2020.107882 PMID: 32834505
66. Sahebi I. G., Masoomi B., \& Ghorbani S. (2020). Expert oriented approach for analyzing the blockchain adoption barriers in humanitarian supply chain. Technology in Society, 63, 1-10. https://doi.org/10. 1016/j.techsoc.2020.101427
67. Polim, R., Hu, Q., \& Kumara, S. (2017). Blockchain in megacity logistics. In IIE Annual Conference. Proceedings (pp. 1589-1594). Institute of Industrial and Systems Engineers (IISE). US.
68. Kamble S., Gunasekaran A., \& Arha H. (2019). Understanding the Blockchain technology adoption in supply chains-Indian context. International Journal of Production Research, 57(7), 2009-2033. https://doi.org/10.1080/00207543.2018.1518610
69. Kim H. M., \& Laskowski M. (2018). Toward an ontology-driven blockchain design for supply-chain provenance. Intelligent Systems in Accounting, Finance and Management, 25(1), 18-27. https://doi. org/10.1002/isaf. 1424
70. Holland M., Nigischer C., \& Stjepandić J. (2017). Copyright protection in additive manufacturing with blockchain approach. In Transdisciplinary Engineering: A Paradigm Shift (pp. 914-921). IOS Press.
71. Pandey V., Pant M., \& Snasel V. (2022). Blockchain technology in food supply chains: Review and bibliometric analysis. Technology in Society, 1-10. https://doi.org/10.1016/j.techsoc.2022.101954

72. Davidson, S., De Filippi, P., \& Potts, J. (2016). Economics of blockchain. SSRN 2744751.
73. Lee J. H., \& Pilkington M. (2017). How the blockchain revolution will reshape the consumer electronics industry [future directions]. IEEE Consumer Electronics Magazine, 6(3), 19-23. https://doi.org/10. 1109/MCE.2017.2684916
74. Siagian H., Tarigan Z. J. H., \& Jie F. (2021). Supply chain integration enables resilience, flexibility, and innovation to improve business performance in COVID-19 era. Sustainability, 13(9), 1-19. https://doi. org/10.3390/su13094669
75. Tiwari S. (2021). Supply chain integration and Industry 4.0: a systematic literature review. Benchmarking: An International Journal, 28(3), 990-1030. https://doi.org/10.1108/BIJ-08-2020-0428
76. Vafaei-Zadeh A., Ramayah T., Hanifah H., Kurnia S., \& Mahmud I. (2020). Supply chain information integration and its impact on the operational performance of manufacturing firms in Malaysia. Information \& Management, 57(8), 1-36. https://doi.org/10.1016/j.im.2020.103386
77. Aunyawong W., Wararatchai P., \& Hotrawaisaya C. (2020). The influence of supply chain integration on supply chain performance of auto-parts manufacturers in Thailand: a mediation approach. International Journal of Supply Chain Management, 9(3), 578-590.
78. Liu C.-L. and Lee M.-Y. (2018). Integration, supply chain resilience, and service performance in thirdparty logistics providers. The International Journal of Logistics Management, 29(1), 5-21. https://doi. org/10.1108/IJLM-11-2016-0283
79. Tarigan Z. J. H., Siagian H., \& Jie F. (2021). Impact of internal integration, supply chain partnership, supply chain agility, and supply chain resilience on sustainable advantage. Sustainability, 13(10), 1-18. https://doi.org/10.3390/su13105460
80. Mandal S. (2021). Impact of supplier innovativeness, top management support and strategic sourcing on supply chain resilience. International Journal of Productivity and Performance Management, 70(7), 1561-1581. https://doi.org/10.1108/IJPPM-07-2019-0349
81. Cui L., Wu H., Wu L., Kumar A., \& Tan K. H. (2022). Investigating the relationship between digital technologies, supply chain integration and firm resilience in the context of COVID-19. Annals of Operations Research, 1-29. https://doi.org/10.1007/s10479-022-04735-y PMID: 35645444
82. Gligor D. M., \& Holcomb M. (2014). The road to supply chain agility: an RBV perspective on the role of logistics capabilities. The International Journal of Logistics Management, 25(1), 160-179. https://doi. org/10.1108/IJLM-07-2012-0062
83. Vijayasarathy L. R. (2010). An investigation of moderators of the link between technology use in the supply chain and supply chain performance. Information \& Management, 47(7-8), 364-371. https://doi.org/10.1016/j.im.2010.08.004
84. Thunyachairat A. (2021). Blockchain technology adoption in supply chain management practices: a conceptual framework. Journal of Kanchanaburi Rajbhat University, 10(2), 169-179.
85. Liu Z., \& Li Z. (2020). A blockchain-based framework of cross-border e-commerce supply chain. International Journal of Information Management, 52, 1-18. https://doi.org/10.1016/j.ijinfomgt.2019. 102059
86. Orji I. J., Kusi-Sarpong S., Huang S., \& Vazquez-Brust D. (2020). Evaluating the factors that influence blockchain adoption in the freight logistics industry. Transportation Research Part E: Logistics and Transportation Review, 141, 1-44. https://doi.org/10.1016/j.tre.2020.102025
87. Wang Y., Singgih M., Wang J., \& Rit M. (2019). Making sense of blockchain technology: How will it transform supply chains?. International Journal of Production Economics, 211, 221-236. https://doi. org/10.1016/j.ijpe.2019.02.002
88. Liu Y., Zhu Q., \& Seuring S. (2020). New technologies in operations and supply chains: Implications for sustainability. International journal of production economics, 229, 1-14. https://doi.org/10.1016/j.ijpe.2020.107889 PMID: 32834507
89. Leal-Millán A., Roldán J.L., Leal-Rodríguez A.L. and Ortega-Gutiérrez J. (2016). IT and relationship learning in networks as drivers of green innovation and customer capital: evidence from the automobile sector. Journal of Knowledge Management, 20(3), 444-464. https://doi.org/10.1108/JKM-05-2015-0203
90. Dillman D. A. (2000). Mail and internet surveys: the tailored design method. NY: John Wiley \& Sons.
91. Podsakoff P. M., MacKenzie S. B., Lee J. Y., \& Podsakoff N. P. (2003). Common method biases in behavioral research: A critical review of the literature and recommended remedies. Journal of Applied Psychology, 88(5), 879-903. https://doi.org/10.1037/0021-9010.88.5.879 PMID: 14516251
92. Podsakoff P. M., MacKenzie S. B., \& Podsakoff N. P. (2012). Sources of method bias in social science research and recommendations on how to control it. Annual review of psychology, 63, 539-569. Retrieved March 22, 2022 from: https://www.annualreviews.org/doi/full/10.1146/annurev-psych-120710-100452. https://doi.org/10.1146/annurev-psych-120710-100452 PMID: 21838546

93. Al-Swidi A. K., Hair J. F., \& Al-Hakimi M. A. (2023). Sustainable development-oriented regulatory and competitive pressures to shift toward a circular economy: The role of environmental orientation and Industry 4.0 technologies. Business Strategy and the Environment, 1-16. https://doi.org/10.1002/bse. 3393
94. Fuller C. M., Simmering M. J., Atinc G., Atinc Y., \& Babin B. J. (2016). Common methods variance detection in business research. Journal of business research, 69(8), 3192-3198. https://doi.org/10. 1016/j.jbusres.2015.12.008
95. Ringle, C. M., Wende, S., \& Will, A. (2005). SmartPLS 2.0 (Beta). November 3, 2020, from: www. smartpls.de.
96. Gelaidan H.M., Al-Swidi A.K. and Al-Hakimi M.A. (2023). Servant and authentic leadership as drivers of innovative work behaviour: the moderating role of creative self-efficacy. European Journal of Innovation Management, In press, 1-29. https://doi.org/10.1108/EJIM-07-2022-0382
97. Henseler J., Ringle C.M. and Sinkovics R.R. (2009). The use of partial least squares path modeling in international marketing. In Sinkovics R.R. and Ghauri P.N. (Ed.) New Challenges to International Marketing (Advances in International Marketing, Vol. 20), Emerald Group Publishing Limited, Bingley (277-319). https://doi.org/10.1108/S1474-7979(2009)0000020014
98. Evermann J., \& Rönkkö M. (2021). Recent developments in PLS. Communications of the Association for Information Systems, 44, 123-132.
99. Reinartz W., Haenlein M., \& Henseler J. (2009). An empirical comparison of the efficacy of covariancebased and variance-based SEM. International Journal of Research in Marketing, 26(4), 332-344. https://doi.org/10.1016/j.ijresmar.2009.08.001
100. Jöreskog K. G., \& Wold H. (1982). The ML and PLS techniques for modeling with latent variables: Historical and comparative aspects. In Jöreskog K. G. \& Wold H. (Eds.), Systems under indirect observation, part I (pp. 263-270). North-Holland.
101. Sosik J. J., Kahai S. S., \& Piovoso M. J. (2009). Silver bullet or voodoo statistics? A primer for using the partial least squares data analytic technique in group and organization research. Group \& Organization Management, 34(1), 5-36. https://doi.org/10.1177/1059601108329198
102. Hair J. F., Howard M., \& Nitzl C. (2020). Assessing measurement model quality in PLS-SEM using confirmatory composite analysis. Journal of Business Research, 109, 101-110. https://doi.org/10. 1016/j.jbusres.2019.11.069
103. Nunnally J. C. \& Bernstein I. (1994). Psychometric theory. ( $3^{\text {rd }}$ ed.), New York, NY: McGraw-Hill Education.
104. Hair J. F., Ringle C. M., \& Sarstedt M. (2011). PLS-SEM: Indeed a silver bullet. Journal of Marketing Theory and Practice, 19(2), 139-151. https://doi.org/http\%3A//dx.doi.org/10.2753/MTP1069-6679190202
105. Henseler J., Ringle C. M., \& Sarstedt M. (2015). A new criterion for assessing discriminant validity in variance-based structural equation modeling. Journal of the academy of marketing science, 43 (1),115-135. https://doi.org/10.1007/s11747-014-0403-8
106. Peng D. X., \& Lai F. (2012). Using partial least squares in operations management research: A practical guideline and summary of past research. Journal of operations management, 30(6), 467-480. https://doi.org/10.1016/j.jom.2012.06.002
107. Sarstedt M., Hair J. F. Jr., Nitzl C., Ringle C. M., \& Howard M. C. (2020). Beyond a tandem analysis of SEM and PROCESS: Use of PLS-SEM for mediation analyses!. International Journal of Market Research, 62(3), 288-299. https://doi.org/10.1177/1470785320915686
108. Chin W. W. (1998). The partial least squares approach to structural equation modeling. In Modern methods for business research, 295(2), 295-336. Psychology Press.
109. Cohen J. (2013). Statistical power analysis for the behavioral sciences. Routledge.
110. Manley S. C., Hair J. F., Williams R. I., \& McDowell W. C. (2021). Essential new PLS-SEM analysis methods for your entrepreneurship analytical toolbox. International Entrepreneurship and Management Journal, 17(1), 1-21. https://doi.org/10.1007/s11365-020-00687-6
111. Ning Y., Li L., Xu S. X., \& Yang S. (2023). How do digital technologies improve supply chain resilience in the COVID-19 pandemic? Evidence from Chinese manufacturing firms. Frontiers of Engineering Management, 10(1), 39-50. https://doi.org/10.1007/s42524-022-0230-4
112. Dubey R., Gunasekaran A., Childe S. J., Roubaud D., Wamba S. F., Giannakis M., et al. (2019). Big data analytics and organizational culture as complements to swift trust and collaborative performance in the humanitarian supply chain. International Journal of Production Economics, 210, 120-136. https://doi.org/10.1016/j.ijpe.2019.01.023
113. Mikalef P., \& Pateli A. (2017). Information technology-enabled dynamic capabilities and their indirect effect on competitive performance: Findings from PLS-SEM and fsQCA. Journal of Business Research, 70, 1-16. https://doi.org/10.1016/j.jbusres.2016.09.004

114. Ying W., Jia S., \& Du W. (2018). Digital enablement of blockchain: Evidence from HNA group. International Journal of Information Management, 39, 1-4. https://doi.org/10.1016/j.ijinfomgt.2017.10.004
115. Yli-Huumo J., Ko D., Choi S., Park S., \& Smolander K. (2016). Where is current research on blockchain technology?-a systematic review. PloS one, 11(10), 1-27. https://doi.org/10.1371/journal.pone. 0163477 PMID: 27695049
116. Saeed H., Malik H., Bashir U., Ahmad A., Riaz S., Ilyas M., et al. (2022). Blockchain technology in healthcare: A systematic review. Plos one, 17(4), 1-31. https://doi.org/10.1371/journal.pone. 0266462 PMID: 35404955
117. Wong L. W., Leong L. Y., Hew J. J., Tan G. W. H., \& Ooi K. B. (2020). Time to seize the digital evolution: Adoption of blockchain in operations and supply chain management among Malaysian SMEs. International Journal of Information Management, 52, 1-19. https://doi.org/10.1016/j.ijinfomgt.2019. 08.005
118. Levis D., Fontana F., \& Ughetto E. (2021). A look into the future of blockchain technology. Plos one, 16(11), 1-20. https://doi.org/10.1371/journal.pone. 0258995 PMID: 34788307
119. Queiroz M. M., \& Wamba S. F. (2019). Blockchain adoption challenges in supply chain: An empirical investigation of the main drivers in India and the USA. International Journal of Information Management, 46, 70-82. https://doi.org/10.1016/j.ijinfomgt.2018.11.021
120. Pattanayak S., Arputham R. M., Goswami M., \& Rana N. P. (2023). Blockchain Technology and Its Relationship With Supply Chain Resilience: A Dynamic Capability Perspective. IEEE Transactions on Engineering Management. In press, 1-15. https://doi.org/10.1109/TEM.2023.3235771
121. Scholten K., Stevenson M. and van Donk D.P. (2020). Dealing with the unpredictable: supply chain resilience. International Journal of Operations \& Production Management, 40(1), 1-10. https://doi.org/10.1108/IJOPM-01-2020-789
122. Han Y., Chong W. K., \& Li D. (2020). A systematic literature review of the capabilities and performance metrics of supply chain resilience. International Journal of Production Research, 58(15), 4541-4566. https://doi.org/10.1080/00207543.2020.1785034
123. Di Vaio A., \& Varriale L. (2020). Blockchain technology in supply chain management for sustainable performance: Evidence from the airport industry. International Journal of Information Management, 52, 1-16. https://doi.org/10.1016/j.ijinfomgt.2019.09.010
124. Ahn M.J., Hajela A. and Akbar M. (2012). High technology in emerging markets: Building biotechnology clusters, capabilities and competitiveness in India. Asia-Pacific Journal of Business Administration, 4(1), 23-41. https://doi.org/10.1108/17574321211207953
125. Guide V. D. R. Jr, \& Ketokivi M. (2015). Notes from the Editors: Redefining some methodological criteria for the journal. Journal of Operations Management, 37(1), 5-8. https://doi.org/10.1016/S0272-6963(15)00056-X
