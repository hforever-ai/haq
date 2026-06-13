"""Seed rights_articles table with 20 constitutional/legal rights in Hindi."""
import psycopg2
from psycopg2.extras import execute_values

DB = "aarambha_haq"

RIGHTS = [
    # ── महिला हक (Women's Rights) ─────────────────────────────────────────
    {
        "slug": "equal-pay",
        "title_hi": "समान वेतन का अधिकार",
        "title_en": "Right to Equal Pay",
        "category": "mahila-haq",
        "summary_hi": "पुरुष और महिला को समान काम के लिए समान वेतन मिलना चाहिए। समान पारिश्रमिक अधिनियम 1976 के तहत यह कानूनी अधिकार है।",
        "detail_hi": """<p><strong>समान पारिश्रमिक अधिनियम, 1976</strong> के अनुसार किसी भी नियोक्ता के लिए एक ही कार्य के लिए महिला और पुरुष को अलग-अलग वेतन देना गैरकानूनी है।</p>
<ul>
  <li>यह अधिकार संविधान के <strong>अनुच्छेद 39(d)</strong> से मिलता है।</li>
  <li>सरकारी व निजी — दोनों क्षेत्रों में लागू।</li>
  <li>उल्लंघन पर नियोक्ता को ₹10,000 जुर्माना या 3 महीने कैद।</li>
</ul>
<p><strong>अगर आपके साथ भेदभाव हो:</strong> श्रम विभाग में शिकायत दर्ज करें। Labour Court में वाद दायर कर सकते हैं।</p>""",
        "keywords": ["equal pay", "वेतन", "भेदभाव", "नौकरी"],
    },
    {
        "slug": "posh-workplace",
        "title_hi": "कार्यस्थल पर यौन उत्पीड़न से सुरक्षा",
        "title_en": "Protection Against Sexual Harassment at Work",
        "category": "mahila-haq",
        "summary_hi": "POSH अधिनियम 2013 के तहत हर महिला कर्मचारी को कार्यस्थल पर सुरक्षित माहौल का अधिकार है। 10+ कर्मचारी वाले संस्थान में ICC होना अनिवार्य है।",
        "detail_hi": """<p><strong>यौन उत्पीड़न (रोकथाम, निषेध और निवारण) अधिनियम, 2013</strong> — POSH Act।</p>
<ul>
  <li>हर 10+ कर्मचारियों वाले संस्थान में <strong>आंतरिक शिकायत समिति (ICC)</strong> अनिवार्य।</li>
  <li>ICC में कम से कम 1 बाहरी महिला सदस्य।</li>
  <li>शिकायत के 90 दिन के भीतर जांच पूरी होनी चाहिए।</li>
  <li>10 से कम कर्मचारियों वाले संस्थान → जिला स्तरीय LCC में शिकायत।</li>
  <li>शिकायतकर्ता की पहचान गुप्त रखी जाती है।</li>
</ul>
<p><strong>शिकायत कैसे करें:</strong> अपनी ICC या जिला अधिकारी (DM/SDM) को लिखित शिकायत दें। ऑनलाइन: SHe-Box पोर्टal (shebox.wcd.gov.in)</p>""",
        "keywords": ["POSH", "यौन उत्पीड़न", "कार्यस्थल", "ICC", "महिला"],
    },
    {
        "slug": "dowry-prohibition",
        "title_hi": "दहेज विरोधी कानून",
        "title_en": "Anti-Dowry Law",
        "category": "mahila-haq",
        "summary_hi": "दहेज लेना और देना दोनों कानूनी अपराध है। दहेज निषेध अधिनियम 1961 और IPC धारा 498A के तहत 7 साल तक की सजा हो सकती है।",
        "detail_hi": """<p><strong>दहेज निषेध अधिनियम, 1961</strong> और <strong>IPC धारा 498A</strong> दोनों मिलकर दहेज को अपराध बनाते हैं।</p>
<ul>
  <li>दहेज देना या लेना दोनों 5 साल + ₹15,000 जुर्माने से दंडनीय।</li>
  <li>IPC 498A: पति या ससुराल द्वारा क्रूरता — 3 साल तक की सजा।</li>
  <li>दहेज मृत्यु (IPC 304B): शादी के 7 साल के भीतर मृत्यु → 7 साल से उम्रकैद।</li>
</ul>
<p><strong>शिकायत कहाँ करें:</strong> नजदीकी पुलिस स्टेशन। महिला हेल्पलाइन: <strong>181</strong>। राष्ट्रीय महिला आयोग: 7827170170।</p>""",
        "keywords": ["दहेज", "498A", "शादी", "ससुराल"],
    },

    # ── घरेलू हिंसा (Domestic Violence) ────────────────────────────────────
    {
        "slug": "domestic-violence-protection",
        "title_hi": "घरेलू हिंसा से सुरक्षा",
        "title_en": "Protection from Domestic Violence",
        "category": "gharelu-hinsa",
        "summary_hi": "घरेलू हिंसा संरक्षण अधिनियम 2005 के तहत महिला शारीरिक, भावनात्मक, यौन या आर्थिक हिंसा से कानूनी सुरक्षा पा सकती है।",
        "detail_hi": """<p><strong>घरेलू हिंसा से महिलाओं का संरक्षण अधिनियम (PWDV Act), 2005</strong></p>
<ul>
  <li>हिंसा के प्रकार: शारीरिक, यौन, भावनात्मक, आर्थिक।</li>
  <li><strong>Protection Order</strong>: कोर्ट हिंसा करने वाले को घर से दूर रहने का आदेश दे सकती है।</li>
  <li><strong>Residence Order</strong>: महिला को साझा घर में रहने का अधिकार।</li>
  <li><strong>Monetary Relief</strong>: खर्च, इलाज, बच्चों की देखभाल का मुआवजा।</li>
  <li>Protection Officer (PO) नि:शुल्क मदद करता है।</li>
</ul>
<p><strong>आपातकालीन मदद:</strong> पुलिस हेल्पलाइन <strong>112</strong>। महिला हेल्पलाइन <strong>181</strong>। वन स्टॉप सेंटर (पोषण 2.0 के तहत)।</p>""",
        "keywords": ["घरेलू हिंसा", "PWDV", "पति", "सुरक्षा"],
    },
    {
        "slug": "maintenance-right",
        "title_hi": "भरण-पोषण का अधिकार",
        "title_en": "Right to Maintenance / Alimony",
        "category": "gharelu-hinsa",
        "summary_hi": "CrPC धारा 125 के तहत पत्नी, बच्चे और माता-पिता को भरण-पोषण का अधिकार है। पति यदि कमाता है तो गुजारा भत्ता देना कानूनी जिम्मेदारी है।",
        "detail_hi": """<p><strong>CrPC धारा 125</strong> — भरण-पोषण का अधिकार।</p>
<ul>
  <li>पत्नी (तलाकशुदा समेत), नाबालिग बच्चे, और अशक्त माता-पिता — सभी पात्र।</li>
  <li>Magistrate कोर्ट में आवेदन करें — वकील की जरूरत नहीं, Legal Aid से भी।</li>
  <li>Interim Maintenance: सुनवाई के दौरान भी अंतरिम राशि मिल सकती है।</li>
  <li>तलाकशुदा मुस्लिम महिला: <strong>Muslim Women (Protection of Rights on Divorce) Act 1986</strong> + Supreme Court के हालिया आदेश।</li>
</ul>
<p><strong>मदद के लिए:</strong> जिला कानूनी सेवा प्राधिकरण (DLSA) — नि:शुल्क वकील। Helpline: 15100</p>""",
        "keywords": ["भरण-पोषण", "गुजारा भत्ता", "Maintenance", "पत्नी", "तलाक"],
    },

    # ── प्रसूति (Maternity) ─────────────────────────────────────────────────
    {
        "slug": "maternity-benefit",
        "title_hi": "मातृत्व लाभ का अधिकार",
        "title_en": "Maternity Benefit Rights",
        "category": "prasuti",
        "summary_hi": "प्रसूति लाभ अधिनियम 1961 के तहत महिला कर्मचारी को प्रसव से पहले 8 हफ्ते और बाद में 18 हफ्ते का सवेतन अवकाश मिलता है।",
        "detail_hi": """<p><strong>मातृत्व लाभ (संशोधन) अधिनियम, 2017</strong></p>
<ul>
  <li>कुल <strong>26 हफ्ते</strong> का वेतन सहित अवकाश (पहले 2 बच्चों के लिए)।</li>
  <li>तीसरे बच्चे से: 12 हफ्ते।</li>
  <li>Surrogacy/Adoption: 12 हफ्ते।</li>
  <li>50+ कर्मचारी वाले दफ्तर में <strong>creche की सुविधा</strong> अनिवार्य।</li>
  <li>Work-from-Home: Manager और कर्मचारी की सहमति से।</li>
  <li>Dismissal प्रतिबंधित — गर्भावस्था के दौरान नौकरी नहीं जा सकती।</li>
</ul>
<p>असंगठित क्षेत्र के लिए: <strong>प्रधानमंत्री मातृ वंदना योजना (PMMVY)</strong> — ₹5,000 पंजीकृत बच्चे के लिए।</p>""",
        "keywords": ["मातृत्व", "Maternity Leave", "प्रसव", "गर्भावस्था", "PMMVY"],
    },

    # ── तलाक/पारिवारिक (Divorce / Family) ─────────────────────────────────
    {
        "slug": "divorce-rights",
        "title_hi": "तलाक और अलगाव के अधिकार",
        "title_en": "Right to Divorce and Separation",
        "category": "talak",
        "summary_hi": "हिंदू विवाह अधिनियम 1955 के तहत महिला क्रूरता, परित्याग, व्यभिचार आदि आधार पर तलाक ले सकती है। मुस्लिम महिला खुला द्वारा।",
        "detail_hi": """<p><strong>हिंदू विवाह अधिनियम, 1955 — धारा 13</strong> के तहत तलाक के आधार:</p>
<ul>
  <li>व्यभिचार (Adultery), क्रूरता (Cruelty), परित्याग (Desertion), धर्मांतरण।</li>
  <li>महिला के अतिरिक्त आधार: बलात्कार, Bigamy, 1955 से पहले बाल विवाह।</li>
  <li>Family Court में याचिका — Legal Aid से नि:शुल्क।</li>
</ul>
<p><strong>मुस्लिम महिला:</strong> खुला (Khula) द्वारा तलाक ले सकती है। <strong>तीन तलाक (Triple Talaq)</strong> अब दंडनीय अपराध — Muslim Women (Protection of Rights on Marriage) Act 2019।</p>
<p><strong>तलाक के बाद:</strong> Maintenance (CrPC 125), बच्चों की Custody, Stridhan वापस लेने का अधिकार।</p>""",
        "keywords": ["तलाक", "Divorce", "खुला", "Triple Talaq", "Alimony"],
    },
    {
        "slug": "triple-talaq-banned",
        "title_hi": "तीन तलाक अब अपराध है",
        "title_en": "Triple Talaq is a Criminal Offence",
        "category": "talak",
        "summary_hi": "2019 के कानून के बाद एक साथ तीन तलाक (तलाक-ए-बिद्दत) अवैध और आपराधिक है। पति को 3 साल की जेल हो सकती है।",
        "detail_hi": """<p><strong>मुस्लिम महिला (विवाह अधिकार संरक्षण) अधिनियम, 2019</strong></p>
<ul>
  <li>एक साथ तीन बार "तलाक" बोलना — मौखिक, लिखित, या इलेक्ट्रॉनिक — गैरकानूनी।</li>
  <li>पति को <strong>3 साल की जेल</strong> और जुर्माना।</li>
  <li>महिला को अपने नाबालिग बच्चों की Custody और Maintenance का अधिकार।</li>
  <li>FIR दर्ज कराने के बाद Magistrate की अनुमति से Bail।</li>
</ul>
<p><strong>शिकायत:</strong> नजदीकी पुलिस स्टेशन में FIR। Helpline: 112 या 181।</p>""",
        "keywords": ["तीन तलाक", "Triple Talaq", "Muslim", "तलाक", "2019"],
    },

    # ── संपत्ति अधिकार (Property Rights) ──────────────────────────────────
    {
        "slug": "property-rights-women",
        "title_hi": "महिला का संपत्ति में अधिकार",
        "title_en": "Women's Property Rights",
        "category": "sampatti",
        "summary_hi": "2005 के संशोधन के बाद हिंदू महिला को पिता की संपत्ति में बेटे के समान अधिकार मिलते हैं। विवाहित-अविवाहित दोनों पात्र।",
        "detail_hi": """<p><strong>हिंदू उत्तराधिकार (संशोधन) अधिनियम, 2005</strong> — धारा 6:</p>
<ul>
  <li>बेटी <strong>Coparcener</strong> (सह-स्वामी) बन गई — बेटे के बराबर अधिकार।</li>
  <li>विवाहित या अविवाहित — दोनों को समान हिस्सा।</li>
  <li>2005 से पहले मृत पिता की संपत्ति पर भी अधिकार (SC: Vineeta Sharma Case 2020)।</li>
  <li>Stridhan (पर्सनल प्रॉपर्टी, गहने, उपहार) पूरी तरह महिला की।</li>
</ul>
<p><strong>अगर हिस्सा न दिया जाए:</strong> Civil Court में Partition Suit। DLSA से नि:शुल्क वकील।</p>""",
        "keywords": ["संपत्ति", "Property", "विरासत", "Coparcener", "पैतृक"],
    },
    {
        "slug": "right-to-shelter",
        "title_hi": "आवास का अधिकार",
        "title_en": "Right to Adequate Housing",
        "category": "sampatti",
        "summary_hi": "संविधान के अनुच्छेद 21 के अंतर्गत आवास का अधिकार जीवन के अधिकार का हिस्सा है। PMAY-G/U जैसी योजनाएं इसे क्रियान्वित करती हैं।",
        "detail_hi": """<p><strong>अनुच्छेद 21</strong> — जीवन और व्यक्तिगत स्वतंत्रता का अधिकार में Supreme Court ने आवास को शामिल किया।</p>
<ul>
  <li><strong>PMAY-G</strong>: ग्रामीण परिवारों को 1.2–1.3 लाख रुपये पक्का घर के लिए।</li>
  <li><strong>PMAY-U</strong>: शहरी क्षेत्र में EWS/LIG के लिए सब्सिडी।</li>
  <li>बेघर करना (Forced Eviction): उचित पुनर्वास के बिना अवैध।</li>
</ul>
<p>अगर सरकारी जमीन पर अवैध कब्जा हटाया जाए तो पुनर्वास का अधिकार है।</p>""",
        "keywords": ["आवास", "Housing", "PMAY", "बेघर", "Eviction"],
    },

    # ── पेंशन/सामाजिक सुरक्षा (Pension / Social Security) ──────────────────
    {
        "slug": "old-age-pension",
        "title_hi": "वृद्धावस्था पेंशन का अधिकार",
        "title_en": "Old Age Pension",
        "category": "pension",
        "summary_hi": "60+ वर्ष के BPL नागरिकों को IGNOAPS के तहत ₹200–500 प्रति माह पेंशन का अधिकार है। राज्य सरकार अतिरिक्त राशि जोड़ती है।",
        "detail_hi": """<p><strong>इंदिरा गांधी राष्ट्रीय वृद्धावस्था पेंशन योजना (IGNOAPS)</strong></p>
<ul>
  <li>पात्रता: 60+ साल, BPL परिवार।</li>
  <li>केंद्र राशि: 60-79 साल → ₹200/माह; 80+ → ₹500/माह।</li>
  <li>कई राज्य ₹1,000-3,000/माह तक देते हैं।</li>
  <li>आवेदन: ग्राम पंचायत / नगर निगम कार्यालय।</li>
  <li>राशन कार्ड, आयु प्रमाण, BPL प्रमाण जरूरी।</li>
</ul>""",
        "keywords": ["पेंशन", "Pension", "वृद्धावस्था", "BPL", "IGNOAPS"],
    },
    {
        "slug": "widow-pension",
        "title_hi": "विधवा पेंशन",
        "title_en": "Widow Pension",
        "category": "pension",
        "summary_hi": "40-79 साल की BPL विधवाओं को IGNWPS के तहत पेंशन मिलती है। इंदिरा गांधी राष्ट्रीय विधवा पेंशन योजना।",
        "detail_hi": """<p><strong>इंदिरा गांधी राष्ट्रीय विधवा पेंशन योजना (IGNWPS)</strong></p>
<ul>
  <li>पात्रता: 40-79 साल, BPL विधवा।</li>
  <li>केंद्र राशि: ₹300/माह। राज्य अतिरिक्त राशि जोड़ते हैं।</li>
  <li>80+ होने पर IGNOAPS में स्वत: convert।</li>
  <li>आवेदन: ग्राम पंचायत / नगर निगम।</li>
  <li>दस्तावेज: पति की मृत्यु प्रमाण पत्र, राशन कार्ड, बैंक खाता।</li>
</ul>""",
        "keywords": ["विधवा", "Widow", "पेंशन", "IGNWPS", "BPL"],
    },
    {
        "slug": "disability-pension",
        "title_hi": "दिव्यांग पेंशन",
        "title_en": "Disability Pension",
        "category": "pension",
        "summary_hi": "18-79 साल के 80%+ दिव्यांगता वाले BPL नागरिकों को IGNDPS के तहत पेंशन। गंभीर/बहु-दिव्यांगता पर भी लाभ।",
        "detail_hi": """<p><strong>इंदिरा गांधी राष्ट्रीय दिव्यांगता पेंशन योजना (IGNDPS)</strong></p>
<ul>
  <li>पात्रता: 18-79 साल, 80%+ दिव्यांगता, BPL।</li>
  <li>राशि: ₹300/माह (केंद्र) + राज्य की टॉप-अप।</li>
  <li>दिव्यांगता प्रमाण पत्र UDID Card से।</li>
  <li>RPWD Act 2016 के तहत 21 प्रकार की दिव्यांगता मान्य।</li>
  <li>आवेदन: ग्राम पंचायत / जिला दिव्यांगजन सशक्तिकरण अधिकारी।</li>
</ul>""",
        "keywords": ["दिव्यांग", "Disability", "पेंशन", "IGNDPS", "UDID"],
    },

    # ── कानूनी सहायता (Legal Aid) ─────────────────────────────────────────
    {
        "slug": "free-legal-aid",
        "title_hi": "नि:शुल्क कानूनी सहायता",
        "title_en": "Free Legal Aid",
        "category": "legal-aid",
        "summary_hi": "कानूनी सेवा प्राधिकरण अधिनियम 1987 के तहत SC/ST, महिला, बच्चे, दिव्यांग, BPL और जेल में बंद लोगों को मुफ्त वकील मिलता है।",
        "detail_hi": """<p><strong>कानूनी सेवा प्राधिकरण अधिनियम, 1987</strong></p>
<p><strong>कौन पात्र है:</strong></p>
<ul>
  <li>SC/ST परिवार।</li>
  <li>महिलाएं और बच्चे।</li>
  <li>दिव्यांग व्यक्ति।</li>
  <li>वार्षिक आय ₹1 लाख से कम।</li>
  <li>हिरासत में या जेल में बंद व्यक्ति।</li>
  <li>Natural Disaster पीड़ित।</li>
</ul>
<p><strong>मदद कहाँ लें:</strong></p>
<ul>
  <li>जिला कानूनी सेवा प्राधिकरण (<strong>DLSA</strong>) — हर जिले में।</li>
  <li>तलुका/तहसील कानूनी सेवा समिति।</li>
  <li>National Legal Services Authority Helpline: <strong>15100</strong></li>
</ul>""",
        "keywords": ["कानूनी सहायता", "Legal Aid", "वकील", "DLSA", "NALSA"],
    },
    {
        "slug": "fir-right",
        "title_hi": "FIR दर्ज करने का अधिकार",
        "title_en": "Right to File FIR",
        "category": "legal-aid",
        "summary_hi": "पुलिस का FIR दर्ज करने से मना करना गैरकानूनी है। CrPC धारा 154 के तहत पीड़ित Zero FIR या SP को शिकायत दे सकता है।",
        "detail_hi": """<p><strong>CrPC धारा 154</strong> — FIR का अधिकार।</p>
<ul>
  <li>Cognizable offence में पुलिस FIR दर्ज करने से मना नहीं कर सकती।</li>
  <li><strong>Zero FIR</strong>: किसी भी थाने में दर्ज कर बाद में संबंधित थाने को भेजा जा सकता है।</li>
  <li>पुलिस FIR न ले तो SP / SSP को लिखित शिकायत।</li>
  <li>या सीधे Magistrate को शिकायत (CrPC 156(3))।</li>
  <li>महिला के विरुद्ध अपराध में महिला पुलिस अधिकारी द्वारा बयान।</li>
</ul>
<p><strong>ऑनलाइन FIR:</strong> अधिकतर राज्यों में cybercrime.gov.in या state police portal पर।</p>""",
        "keywords": ["FIR", "पुलिस", "Zero FIR", "CrPC 154", "शिकायत"],
    },
    {
        "slug": "arrest-rights",
        "title_hi": "गिरफ्तारी पर आपके अधिकार",
        "title_en": "Rights on Arrest",
        "category": "legal-aid",
        "summary_hi": "गिरफ्तारी पर पुलिस कारण बताने और वकील से मिलने देने के लिए बाध्य है। अनुच्छेद 22 और CrPC 41B के तहत यह मौलिक अधिकार है।",
        "detail_hi": """<p><strong>संविधान का अनुच्छेद 22</strong> और <strong>CrPC धारा 41B</strong>:</p>
<ul>
  <li>गिरफ्तारी का कारण बताना अनिवार्य।</li>
  <li>अपनी पसंद के वकील से मिलने का अधिकार।</li>
  <li>24 घंटे में Magistrate के सामने पेश करना अनिवार्य।</li>
  <li>गिरफ्तारी की जानकारी परिजनों को देना जरूरी।</li>
  <li>महिला: सूर्योदय से सूर्यास्त के बाद गिरफ्तारी नहीं, महिला पुलिस होनी चाहिए।</li>
  <li>Handcuff केवल विशेष परिस्थिति में।</li>
</ul>
<p><strong>अगर अधिकार का उल्लंघन हो:</strong> High Court में Habeas Corpus याचिका।</p>""",
        "keywords": ["गिरफ्तारी", "Arrest", "Article 22", "CrPC", "वकील"],
    },

    # ── शिक्षा/रोजगार (Education / Employment Rights) ──────────────────────
    {
        "slug": "rte-education",
        "title_hi": "शिक्षा का अधिकार (RTE)",
        "title_en": "Right to Education",
        "category": "shiksha-rozgar",
        "summary_hi": "6-14 साल के सभी बच्चों को मुफ्त और अनिवार्य शिक्षा का अधिकार है। RTE अधिनियम 2009 के तहत निजी स्कूलों में भी 25% सीट EWS के लिए।",
        "detail_hi": """<p><strong>शिक्षा का अधिकार अधिनियम (RTE), 2009</strong></p>
<ul>
  <li>6-14 साल के बच्चों को नजदीकी सरकारी स्कूल में नि:शुल्क पढ़ाई।</li>
  <li>निजी स्कूलों में <strong>25% सीट EWS/Disadvantaged</strong> बच्चों के लिए आरक्षित।</li>
  <li>कोई भी स्कूल Admission के लिए Donation, Capitation Fee या Interview नहीं ले सकता।</li>
  <li>Corporal Punishment प्रतिबंधित।</li>
  <li>Grade 8 तक No Detention Policy।</li>
</ul>
<p><strong>25% EWS Admission:</strong> Udaan Portal (कई राज्यों में ऑनलाइन आवेदन)। अपने राज्य के शिक्षा विभाग की वेबसाइट देखें।</p>""",
        "keywords": ["RTE", "शिक्षा", "स्कूल", "EWS", "25%"],
    },
    {
        "slug": "rti-right",
        "title_hi": "सूचना का अधिकार (RTI)",
        "title_en": "Right to Information (RTI)",
        "category": "shiksha-rozgar",
        "summary_hi": "RTI अधिनियम 2005 के तहत कोई भी नागरिक सरकारी दफ्तर से 30 दिन में जानकारी मांग सकता है। आवेदन शुल्क मात्र ₹10।",
        "detail_hi": """<p><strong>सूचना का अधिकार अधिनियम, 2005</strong></p>
<ul>
  <li>कोई भी भारतीय नागरिक किसी भी सरकारी विभाग से जानकारी मांग सकता है।</li>
  <li>30 दिन में जवाब देना अनिवार्य। जीवन-मृत्यु मामलों में 48 घंटे।</li>
  <li>आवेदन शुल्क: ₹10 (BPL के लिए नि:शुल्क)।</li>
  <li>जवाब न मिले तो First Appellate Authority → CIC/SIC में अपील।</li>
</ul>
<p><strong>ऑनलाइन RTI:</strong> rtionline.gov.in (केंद्र सरकार)। राज्य विभागों के लिए राज्य पोर्टल।</p>""",
        "keywords": ["RTI", "सूचना", "सरकार", "Information", "जानकारी"],
    },
    {
        "slug": "mgnrega-work-right",
        "title_hi": "मनरेगा में काम का अधिकार",
        "title_en": "MGNREGA Right to Work",
        "category": "shiksha-rozgar",
        "summary_hi": "मनरेगा के तहत ग्रामीण परिवार को 100 दिन रोजगार की गारंटी है। आवेदन के 15 दिन में काम न मिले तो Unemployment Allowance मिलता है।",
        "detail_hi": """<p><strong>महात्मा गांधी राष्ट्रीय ग्रामीण रोजगार गारंटी अधिनियम (MGNREGA), 2005</strong></p>
<ul>
  <li>ग्रामीण परिवार को प्रति वित्त वर्ष <strong>100 दिन रोजगार</strong> की कानूनी गारंटी।</li>
  <li>आवेदन के 15 दिन में काम मिलना चाहिए, नहीं मिलने पर बेरोजगारी भत्ता।</li>
  <li>1/3 काम महिलाओं के लिए आरक्षित।</li>
  <li>काम घर से 5 km के भीतर, अधिक दूरी पर 10% अतिरिक्त मजदूरी।</li>
  <li>Job Card के लिए ग्राम पंचायत में आवेदन।</li>
</ul>
<p><strong>Online:</strong> mnregaweb2.nic.in पर Job Card, Payment Status देखें।</p>""",
        "keywords": ["मनरेगा", "MGNREGA", "रोजगार", "Job Card", "100 दिन"],
    },
]


def main():
    conn = psycopg2.connect(dbname=DB)
    cur  = conn.cursor()

    rows = [
        (
            r["slug"], r["title_hi"], r["title_en"], r["category"],
            r["summary_hi"], r["detail_hi"], r["keywords"],
        )
        for r in RIGHTS
    ]

    execute_values(cur, """
        INSERT INTO rights_articles
          (slug, title_hi, title_en, category, summary_hi, detail_hi, keywords)
        VALUES %s
        ON CONFLICT (slug) DO UPDATE SET
          title_hi   = EXCLUDED.title_hi,
          title_en   = EXCLUDED.title_en,
          category   = EXCLUDED.category,
          summary_hi = EXCLUDED.summary_hi,
          detail_hi  = EXCLUDED.detail_hi,
          keywords   = EXCLUDED.keywords
    """, rows)

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Seeded {len(rows)} rights articles")
    print("Categories:", {r["category"] for r in RIGHTS})


if __name__ == "__main__":
    main()
