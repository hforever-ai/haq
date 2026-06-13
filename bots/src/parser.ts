/**
 * parser.ts — Rule-based NLP profile extractor
 * Uses: fuse.js (state fuzzy), didyoumean2 (caste/flag typos), nspell (English spell-correct)
 */
import Fuse from 'fuse.js';
import didYouMean, { ReturnTypeEnums } from 'didyoumean2';
import nspell from 'nspell';

export interface Profile {
  age: number | null;
  gender: string;
  state: string;
  caste: string;
  income: number;
  flags: string[];
}

// ── State data ────────────────────────────────────────────────────────────────
const STATE_MAP: Record<string, string> = {
  'up': 'Uttar Pradesh', 'uttar pradesh': 'Uttar Pradesh',
  'mp': 'Madhya Pradesh', 'madhya pradesh': 'Madhya Pradesh',
  'mh': 'Maharashtra', 'maharashtra': 'Maharashtra',
  'rj': 'Rajasthan', 'rajasthan': 'Rajasthan',
  'wb': 'West Bengal', 'west bengal': 'West Bengal',
  'br': 'Bihar', 'bihar': 'Bihar',
  'tn': 'Tamil Nadu', 'tamil nadu': 'Tamil Nadu',
  'ka': 'Karnataka', 'karnataka': 'Karnataka',
  'gj': 'Gujarat', 'gujarat': 'Gujarat',
  'ap': 'Andhra Pradesh', 'andhra pradesh': 'Andhra Pradesh',
  'ts': 'Telangana', 'telangana': 'Telangana',
  'od': 'Odisha', 'odisha': 'Odisha', 'orissa': 'Odisha',
  'kl': 'Kerala', 'kerala': 'Kerala',
  'pb': 'Punjab', 'punjab': 'Punjab',
  'hr': 'Haryana', 'haryana': 'Haryana',
  'jh': 'Jharkhand', 'jharkhand': 'Jharkhand',
  'cg': 'Chhattisgarh', 'chhattisgarh': 'Chhattisgarh',
  'uk': 'Uttarakhand', 'uttarakhand': 'Uttarakhand',
  'hp': 'Himachal Pradesh', 'himachal pradesh': 'Himachal Pradesh',
  'as': 'Assam', 'assam': 'Assam',
  'jk': 'Jammu and Kashmir', 'jammu kashmir': 'Jammu and Kashmir',
  'dl': 'Delhi', 'delhi': 'Delhi',
  'ga': 'Goa', 'goa': 'Goa',
  'sk': 'Sikkim', 'sikkim': 'Sikkim',
  'mn': 'Manipur', 'manipur': 'Manipur',
  'ml': 'Meghalaya', 'meghalaya': 'Meghalaya',
  'tr': 'Tripura', 'tripura': 'Tripura',
  'nl': 'Nagaland', 'nagaland': 'Nagaland',
  'mz': 'Mizoram', 'mizoram': 'Mizoram',
  'ar': 'Arunachal Pradesh', 'arunachal pradesh': 'Arunachal Pradesh',
  'py': 'Puducherry', 'puducherry': 'Puducherry', 'pondicherry': 'Puducherry',
  'pondichery': 'Puducherry', 'pondicheri': 'Puducherry', 'pondy': 'Puducherry',
  'ch': 'Chandigarh', 'chandigarh': 'Chandigarh',
  'ld': 'Ladakh', 'ladakh': 'Ladakh',
  'dd': 'Dadra and Nagar Haveli', 'daman': 'Daman and Diu',
  'an': 'Andaman and Nicobar', 'lk': 'Lakshadweep',
};

// ── Multilingual tables (all 11 bot languages) ───────────────────────────────
// State names in regional scripts → canonical English name
const STATE_MULTILANG: Record<string, string> = {
  // Bengali (বাংলা)
  'পশ্চিমবঙ্গ': 'West Bengal', 'উত্তর প্রদেশ': 'Uttar Pradesh',
  'বিহার': 'Bihar', 'রাজস্থান': 'Rajasthan', 'মহারাষ্ট্র': 'Maharashtra',
  'মধ্যপ্রদেশ': 'Madhya Pradesh', 'গুজরাত': 'Gujarat', 'অসম': 'Assam',
  'ওড়িশা': 'Odisha', 'কেরল': 'Kerala', 'পঞ্জাব': 'Punjab',
  'হরিয়ানা': 'Haryana', 'ঝাড়খণ্ড': 'Jharkhand', 'দিল্লি': 'Delhi',
  'তামিলনাড়ু': 'Tamil Nadu', 'কর্ণাটক': 'Karnataka', 'অন্ধ্র': 'Andhra Pradesh',
  'তেলেঙ্গানা': 'Telangana', 'ছত্তিসগড়': 'Chhattisgarh', 'উত্তরাখণ্ড': 'Uttarakhand',
  // Telugu (తెలుగు)
  'ఆంధ్రప్రదేశ్': 'Andhra Pradesh', 'తెలంగాణ': 'Telangana',
  'కర్ణాటక': 'Karnataka', 'తమిళనాడు': 'Tamil Nadu',
  'మహారాష్ట్ర': 'Maharashtra', 'కేరళ': 'Kerala', 'ఒడిశా': 'Odisha',
  'పశ్చిమ బెంగాల్': 'West Bengal', 'ఉత్తర ప్రదేశ్': 'Uttar Pradesh',
  // Tamil (தமிழ்)
  'தமிழ்நாடு': 'Tamil Nadu', 'கேரளம்': 'Kerala',
  'கர்நாடகம்': 'Karnataka', 'ஆந்திரா': 'Andhra Pradesh',
  'மகாராஷ்டிரா': 'Maharashtra', 'தெலங்கானா': 'Telangana',
  // Gujarati (ગુજરાતી)
  'ગુજરાત': 'Gujarat', 'રાજસ્થાન': 'Rajasthan',
  'મહારાષ્ટ્ર': 'Maharashtra', 'મધ્ય પ્રદેશ': 'Madhya Pradesh',
  'ઉત્તર પ્રદેશ': 'Uttar Pradesh', 'ગોવા': 'Goa',
  // Kannada (ಕನ್ನಡ)
  'ಕರ್ನಾಟಕ': 'Karnataka', 'ಕೇರಳ': 'Kerala',
  'ತಮಿಳುನಾಡು': 'Tamil Nadu', 'ಆಂಧ್ರ ಪ್ರದೇಶ': 'Andhra Pradesh',
  'ಮಹಾರಾಷ್ಟ್ರ': 'Maharashtra', 'ತೆಲಂಗಾಣ': 'Telangana',
  // Punjabi (ਪੰਜਾਬੀ)
  'ਪੰਜਾਬ': 'Punjab', 'ਹਰਿਆਣਾ': 'Haryana',
  'ਰਾਜਸਥਾਨ': 'Rajasthan', 'ਉੱਤਰ ਪ੍ਰਦੇਸ਼': 'Uttar Pradesh',
  'ਦਿੱਲੀ': 'Delhi', 'ਹਿਮਾਚਲ': 'Himachal Pradesh',
  // Malayalam (മലയാളം)
  'കേരളം': 'Kerala', 'തമിഴ്‌നാട്': 'Tamil Nadu',
  'കർണ്ണാടക': 'Karnataka', 'ആന്ധ്ര': 'Andhra Pradesh',
  // Odia (ଓଡ଼ିଆ)
  'ଓଡ଼ିଶା': 'Odisha', 'ପଶ୍ଚିମ ବଙ୍ଗ': 'West Bengal',
  'ଝାଡ଼ଖଣ୍ଡ': 'Jharkhand', 'ଛତ୍ତିଶଗଡ଼': 'Chhattisgarh',
  // Marathi (Devanagari — distinct from Hindi spellings)
  'महाराष्ट्र': 'Maharashtra', 'गुजरात': 'Gujarat', 'राजस्थान': 'Rajasthan',
  'मध्य प्रदेश': 'Madhya Pradesh', 'उत्तर प्रदेश': 'Uttar Pradesh',
  'पश्चिम बंगाल': 'West Bengal', 'ओडिशा': 'Odisha',
  'पंजाब': 'Punjab', 'हरियाणा': 'Haryana', 'कर्नाटक': 'Karnataka',
  'केरळ': 'Kerala', 'तामिळनाडू': 'Tamil Nadu',
  'आंध्र प्रदेश': 'Andhra Pradesh', 'तेलंगणा': 'Telangana',
  'उत्तराखंड': 'Uttarakhand', 'झारखंड': 'Jharkhand',
  'छत्तीसगड': 'Chhattisgarh', 'हिमाचल प्रदेश': 'Himachal Pradesh',
  'आसाम': 'Assam', 'गोवा': 'Goa', 'दिल्ली': 'Delhi',
};

// Female markers in all 11 scripts
const FEMALE_NATIVE = [
  // Marathi (Devanagari — same script as Hindi)
  'बाई', 'मुलगी', 'महिला',
  // Bengali
  'মহিলা', 'মেয়ে', 'বিধবা', 'গর্ভবতী',
  // Telugu
  'మహిళ', 'మహిళలు', 'వితంతువు', 'గర్భిణి',
  // Tamil
  'பெண்', 'விதவை', 'கர்ப்பிணி',
  // Gujarati
  'સ્ત્રી', 'વિધવા',
  // Kannada
  'ಮಹಿಳೆ', 'ವಿಧವೆ', 'ಗರ್ಭಿಣಿ',
  // Punjabi
  'ਔਰਤ', 'ਵਿਧਵਾ',
  // Malayalam
  'സ്ത്രീ', 'വിധവ', 'ഗർഭിണി',
  // Odia
  'ମହିଳା', 'ବିଧବା', 'ଗର୍ଭବତୀ',
];

// Male markers in all 11 scripts
const MALE_NATIVE = [
  // Marathi
  'पुरुष', 'मुलगा', 'शेतकरी',
  // Bengali
  'পুরুষ', 'কৃষক',
  // Telugu
  'పురుషుడు', 'రైతు',
  // Tamil
  'ஆண்', 'விவசாயி',
  // Gujarati
  'પુરુષ', 'ખેડૂત',
  // Kannada
  'ಪುರುಷ', 'ರೈತ',
  // Punjabi
  'ਮਰਦ', 'ਕਿਸਾਨ',
  // Malayalam
  'പുരുഷൻ', 'കർഷകൻ',
  // Odia
  'ପୁରୁଷ', 'ଚାଷୀ',
];

// Age unit words in all scripts — matches "35 বছর", "45 వయసు"
const AGE_UNIT_NATIVE = [
  'বছর', 'সাল',           // Bengali
  'సంవత్సరాల', 'ఏళ్ళు', 'వయసు', // Telugu
  'வயது',               // Tamil
  'વર્ષ',               // Gujarati
  'ವರ್ಷ',               // Kannada
  'ਸਾਲ',               // Punjabi
  'വർഷം',              // Malayalam
  'ବର୍ଷ',               // Odia
];
const AGE_NATIVE_RE = new RegExp(
  `(\\d{1,3})\\s*(?:${AGE_UNIT_NATIVE.join('|')})`, 'u'
);

// Crore in all scripts — matches "2 crore", "3 কোটি"
const CRORE_NATIVE_TERMS = [
  'करोड़', 'কোটি', 'కోటి', 'கோடி', 'કરોડ', 'ಕೋಟಿ', 'ਕਰੋੜ', 'കോടി', 'କୋଟି',
];
const CRORE_ALL_RE = new RegExp(
  `(\\d+(?:\\.\\d+)?)\\s*(?:crore|${CRORE_NATIVE_TERMS.join('|')})`, 'iu'
);

// Lakh in all scripts — matches "3 লক্ষ", "2 లక్ష"
const LAKH_NATIVE_TERMS = [
  'লক্ষ', 'লাখ',         // Bengali
  'లక్ష',               // Telugu
  'லட்சம்',             // Tamil
  'લાખ',               // Gujarati
  'ಲಕ್ಷ',               // Kannada
  'ਲੱਖ',               // Punjabi
  'ലക്ഷം',              // Malayalam
  'ଲକ୍ଷ',               // Odia
];
const LAKH_NATIVE_RE = new RegExp(
  `(\\d+(?:\\.\\d+)?)\\s*(?:${LAKH_NATIVE_TERMS.join('|')})`, 'u'
);

// Thousand in all scripts
const HAZAAR_NATIVE_TERMS = [
  'হাজার',              // Bengali
  'వేయి', 'వేలు',       // Telugu
  'ஆயிரம்',            // Tamil
  'હજાર',              // Gujarati
  'ಸಾವಿರ',             // Kannada
  'ਹਜ਼ਾਰ',             // Punjabi
  'ആയിരം',             // Malayalam
  'ହଜାର',              // Odia
];
const HAZAAR_NATIVE_RE = new RegExp(
  `(\\d+(?:\\.\\d+)?)\\s*(?:${HAZAAR_NATIVE_TERMS.join('|')})`, 'u'
);

// Caste in regional scripts
const CASTE_NATIVE: Array<[string[], string]> = [
  [['তফসিলি জাতি', 'দলিত', 'ఎస్సీ', 'அட்டவணை சாதி', 'ਅਨੁਸੂਚਿਤ ਜਾਤੀ', 'ഷെഡ്യൂൾഡ് ജാതി', 'ଅନୁସୂଚିତ ଜାତି'], 'SC'],
  [['তফসিলি উপজাতি', 'আদিবাসী', 'ఎస్టీ', 'பழங்குடியினர்', 'ਅਨੁਸੂਚਿਤ ਜਨਜਾਤੀ', 'ഷെഡ്യൂൾഡ് ഗോത്രം', 'ଆଦିବାସୀ'], 'ST'],
  [['অন্যান্য অনগ্রসর', 'ওবিসি', 'ఓబీసీ', 'பிற்படுத்தப்பட்ட', 'ਪਿੱਛੜਾ ਵਰਗ', 'പിന്നോക്ക', 'ପଛୁଆ ବର୍ଗ'], 'OBC'],
  [['সাধারণ', 'సాధారణ', 'பொது', 'ਸਾਧਾਰਣ', 'ಸಾಮಾನ್ಯ', 'സാധാരണ', 'ସାଧାରଣ'], 'General'],
  [['আর্থিকভাবে দুর্বল', 'ఆర్థికంగా బలహీన', 'பொருளாதார ரீதியாக பலவீனமான', 'આર્થિક રીતે નબળા', 'ಆರ್ಥಿಕವಾಗಿ ದುರ್ಬಲ', 'ਆਰਥਿਕ ਕਮਜ਼ੋਰ', 'സാമ്പത്തിക ദുർബല', 'ଆର୍ଥିକ ଦୁର୍ବଳ'], 'EWS'],
];

const STATE_HINDI: Record<string, string> = {
  'उत्तर प्रदेश': 'Uttar Pradesh', 'यूपी': 'Uttar Pradesh',
  'मध्य प्रदेश': 'Madhya Pradesh', 'एमपी': 'Madhya Pradesh',
  'महाराष्ट्र': 'Maharashtra', 'राजस्थान': 'Rajasthan',
  'बिहार': 'Bihar', 'गुजरात': 'Gujarat', 'तमिलनाडु': 'Tamil Nadu',
  'कर्नाटक': 'Karnataka', 'पश्चिम बंगाल': 'West Bengal',
  'हरियाणा': 'Haryana', 'पंजाब': 'Punjab', 'केरल': 'Kerala',
  'उत्तराखंड': 'Uttarakhand', 'झारखंड': 'Jharkhand',
  'छत्तीसगढ़': 'Chhattisgarh', 'हिमाचल': 'Himachal Pradesh',
  'असम': 'Assam', 'दिल्ली': 'Delhi', 'गोवा': 'Goa',
  'तेलंगाना': 'Telangana', 'आंध्र': 'Andhra Pradesh',
  'ओडिशा': 'Odisha', 'पुदुचेरी': 'Puducherry',
  'चंडीगढ़': 'Chandigarh', 'लद्दाख': 'Ladakh',
  'अंडमान': 'Andaman and Nicobar', 'लक्षद्वीप': 'Lakshadweep',
  'दादरा': 'Dadra and Nagar Haveli', 'दमन': 'Daman and Diu',
};

// Deduplicated canonical state names
const STATE_LIST = [...new Set(Object.values(STATE_MAP))];
// Nospace variants: "andrapradesh" → "Andhra Pradesh"
const STATE_LIST_NOSPACE = STATE_LIST.map(s => s.toLowerCase().replace(/\s+/g, ''));

// fuse.js index — handles "rajsthan", "jharkand", multi-word partial matches
const stateFuse = new Fuse(STATE_LIST, {
  includeScore: true,
  threshold: 0.35,   // 0 = exact, 1 = anything; 0.35 balances typo vs false-positive
  minMatchCharLength: 3,
});

// ── Hindi number words ────────────────────────────────────────────────────────
const HINDI_NUM_MAP: Record<string, number> = {
  ek: 1, do: 2, teen: 3, tin: 3, char: 4, chaar: 4,
  paanch: 5, panch: 5, chhe: 6, chheh: 6,
  saat: 7, aath: 8, nau: 9, das: 10,
  gyarah: 11, barah: 12, terah: 13, chaudah: 14, pandrah: 15,
  solah: 16, satrah: 17, atharah: 18, unnees: 19,
  bees: 20, bis: 20, ikkees: 21, baees: 22, pachees: 25,
  tees: 30, chalees: 40, chalis: 40,
  pachaas: 50, pachas: 50, saath: 60, sattar: 70, assi: 80, nabbe: 90,
};
const _numAlt = Object.keys(HINDI_NUM_MAP).join('|');
// "tees saal", "pachas saal" → age
const HINDI_AGE_RE = new RegExp(`\\b(${_numAlt})\\s+(?:saal|sal|sāl|year|yr|yrs|वर्ष)`, 'i');
// "ek lakh", "do lakh" → income
const HINDI_LAKH_RE = new RegExp(`\\b(${_numAlt})\\s+(?:lakh|लाख|lac)`, 'i');
// "paanch hazaar", "das hazar" → income
const HINDI_HAZAAR_RE = new RegExp(`\\b(${_numAlt})\\s+(?:hazaar|hazar|hajar|हजार|हज़ार)`, 'i');

// ── Spell checker (loaded once at startup) ────────────────────────────────────
let spell: ReturnType<typeof nspell> | null = null;

export async function initParser(): Promise<void> {
  try {
    // dynamic import required: dictionary-en v4 is ESM, nspell is CJS
    const dict = await import('dictionary-en').then(m => m.default ?? m);
    const d = dict as { aff: Uint8Array; dic: Uint8Array };
    spell = nspell({ aff: Buffer.from(d.aff), dic: Buffer.from(d.dic) });
  } catch {
    // graceful — bot works without spell checker
  }
}

/** Fix an English word if it's misspelled. Returns original on any doubt. */
function spellFix(word: string): string {
  if (!spell || word.length < 4) return word;
  if (spell.correct(word)) return word;
  const suggestions = spell.suggest(word);
  return suggestions.length > 0 ? suggestions[0] : word;
}

export function normalizeState(raw: string): string {
  const key = raw.trim().toLowerCase();
  return STATE_MAP[key] ?? raw.replace(/\b\w/g, c => c.toUpperCase());
}

// ── State detection ───────────────────────────────────────────────────────────
// Hindi particles and English stop-words that must NOT match state codes
const STATE_SKIP = new Set([
  // Hindi pronouns / particles
  'ka', 'ki', 'ke', 'se', 'me', 'ko', 'ne', 'hi', 'to', 'bhi', 'aur',
  'kya', 'ek', 'hai', 'hun', 'hoo', 'mai', 'main', 'mein', 'hoon',
  'mera', 'mere', 'meri', 'yeh', 'wo', 'woh', 'ye',
  // English stop-words
  'the', 'and', 'for', 'are', 'was', 'has', 'man', 'age', 'girl',
  'boy', 'she', 'her', 'his', 'am', 'an', 'a', 'i', 'old', 'from',
  // Caste/flag codes — handled elsewhere
  'sc', 'st', 'obc', 'ews', 'bpl',
]);

function detectState(text: string): string | null {
  const low = text.toLowerCase();

  // 0. Multilingual scripts (substring — word boundaries unreliable for Unicode)
  for (const [term, canonical] of Object.entries(STATE_MULTILANG)) {
    if (text.includes(term)) return canonical;
  }

  // 1. Hindi aliases (exact token)
  for (const [alias, canonical] of Object.entries(STATE_HINDI)) {
    if (low.includes(alias.toLowerCase())) return canonical;
  }

  // Build word and two-word candidate tokens
  const words = low.split(/[\s,।;/]+/).filter(w => w.length >= 2 && !STATE_SKIP.has(w));
  const candidates: string[] = [...words];
  for (let i = 0; i < words.length - 1; i++) {
    candidates.push(`${words[i]} ${words[i + 1]}`);
  }

  for (const candidate of candidates) {
    // 2. Exact STATE_MAP key
    if (STATE_MAP[candidate]) return STATE_MAP[candidate];

    // 3. Nospace match — "andrapradesh" → "Andhra Pradesh"
    if (candidate.length >= 6) {
      const nsi = STATE_LIST_NOSPACE.indexOf(candidate.replace(/\s+/g, ''));
      if (nsi !== -1) return STATE_LIST[nsi];
    }

    // 4. Fuse.js fuzzy — handles "rajsthan", "himachal pardesh"
    if (candidate.length >= 4) {
      const results = stateFuse.search(candidate);
      if (results.length > 0 && (results[0].score ?? 1) < 0.30) {
        return results[0].item;
      }
    }
  }

  return null;
}

// ── Caste detection ───────────────────────────────────────────────────────────
const CASTE_RE: [RegExp, string][] = [
  [/\bsc\b|scheduled\s+caste|दलित|अनुसूचित\s*जाति/i, 'SC'],
  [/\bst\b|scheduled\s+tribe|आदिवासी|अनुसूचित\s*जनजाति/i, 'ST'],
  [/\bobc\b|other\s+backward|पिछड़ा|पिछड़े|अति\s*पिछड़ा|most\s+backward/i, 'OBC'],
  [/\bews\b|economically\s+weaker|ईडब्ल्यूएस/i, 'EWS'],
  [/\bgeneral\b|\bunreserved\b|सामान्य/i, 'General'],
];
const CASTE_CANDIDATES = ['sc', 'st', 'obc', 'ews', 'general'];
const CASTE_LABEL: Record<string, string> = { sc: 'SC', st: 'ST', obc: 'OBC', ews: 'EWS', general: 'General' };

function detectCaste(text: string): string | null {
  for (const [re, label] of CASTE_RE) {
    if (re.test(text)) return label;
  }
  // Native script caste keywords (Bengali/Telugu/Tamil/Punjabi/Malayalam/Odia)
  for (const [terms, label] of CASTE_NATIVE) {
    if (terms.some(t => text.includes(t))) return label;
  }
  // didyoumean2 — handles "obcc"→OBC, "scc"→SC, "genral"→General
  for (const word of (text.toLowerCase().match(/\b[a-z]{2,10}\b/g) ?? [])) {
    const fixed = spellFix(word); // nspell pre-correction
    const match = didYouMean(fixed, CASTE_CANDIDATES, {
      returnType: ReturnTypeEnums.FIRST_CLOSEST_MATCH,
      threshold: 0.65,
    }) as string | null;
    if (match) return CASTE_LABEL[match];
  }
  return null;
}

// ── Flag detection ────────────────────────────────────────────────────────────
const FLAG_RE: [RegExp, string][] = [
  [/\bwid\w{1,4}\b|विधवा|vidhwa|bidhwa|पति नहीं/i, 'widow'],
  [/\bdisabilit\w+\b|\bdisabled\b|\bhandicap\w*\b|दिव्यांग|विकलांग/i, 'disability'],
  [/\bminority\b|\bmuslim\b|\bchristian\b|\bsikh\b|अल्पसंख्यक/i, 'minority'],
  [/\bbpl\b|गरीबी रेखा|below poverty|\bantyodaya\b|अंत्योदय|\byellow\s*card\b|\bgareeb\b|\bgaribi\b/i, 'bpl'],
  [/\bpregnant\b|\bpregnancy\b|गर्भवती|प्रेग्नेंट/i, 'pregnant'],
  [/\bsenior\s+citizen\b|वृद्ध|बुजुर्ग|वरिष्ठ\s*नागरिक|ज्येष्ठ नागरिक/i, 'senior_citizen'],
  [/\bkisan\b|\bfarmer\b|\bkrishi\b|किसान|कृषक|ರೈತ|রায়তু|விவசாயி|ಕ್ಷೇತ್ರ/i, 'farmer'],
  [/\bex[- ]serviceman\b|\bex[- ]army\b|भूतपूर्व\s+सैनिक|पूर्व\s+सैनिक/i, 'ex_serviceman'],
  [/\borphan\b|अनाथ|निराश्रित/i, 'orphan'],
  [/\blandless\b|भूमिहीन|जमीन\s+नहीं|निर्भूमि/i, 'landless'],
];
const FLAG_CANDIDATES = [
  'disability', 'disabled', 'pregnant', 'widow', 'minority', 'bpl',
  'senior_citizen', 'farmer', 'ex_serviceman', 'orphan', 'landless',
];
const FLAG_LABEL: Record<string, string> = {
  disability: 'disability', disabled: 'disability',
  pregnant: 'pregnant', widow: 'widow',
  minority: 'minority', bpl: 'bpl',
  senior_citizen: 'senior_citizen', farmer: 'farmer',
  ex_serviceman: 'ex_serviceman', orphan: 'orphan', landless: 'landless',
};

function detectFlags(text: string): string[] {
  const flags: string[] = [];
  for (const [re, label] of FLAG_RE) {
    if (re.test(text)) flags.push(label);
  }
  // didyoumean2 — handles "disbled"→disability, "pregnent"→pregnant
  for (const word of (text.toLowerCase().match(/\b[a-z]{4,12}\b/g) ?? [])) {
    const fixed = spellFix(word);
    const match = didYouMean(fixed, FLAG_CANDIDATES, {
      returnType: ReturnTypeEnums.FIRST_CLOSEST_MATCH,
      threshold: 0.72,
    }) as string | null;
    if (match) {
      const flag = FLAG_LABEL[match];
      if (flag && !flags.includes(flag)) flags.push(flag);
    }
  }
  return [...new Set(flags)];
}

// ── Main parser ───────────────────────────────────────────────────────────────
export function parseProfile(text: string): Profile | null {
  // Age (digit form)
  let age: number | null = null;
  const ageMatch = text.match(
    /(?:age|उम्र|āyu|i\s+am)\s*[:\-]?\s*(\d{1,3})|(\d{1,3})\s*(?:साल|saal|sal|year|yr|yrs|वर्ष)/i,
  );
  if (ageMatch) {
    const val = parseInt(ageMatch[1] ?? ageMatch[2]);
    if (val >= 1 && val <= 120) age = val;
  }
  // Age (Hindi word form): "tees saal"→30, "pachas saal"→50
  if (age === null) {
    const wm = text.match(HINDI_AGE_RE);
    if (wm) {
      const val = HINDI_NUM_MAP[wm[1].toLowerCase()];
      if (val && val >= 1 && val <= 100) age = val;
    }
  }
  // Age (native scripts): "35 বছর", "45 వయసు", "28 வயது"
  if (age === null) {
    const nm = text.match(AGE_NATIVE_RE);
    if (nm) {
      const val = parseInt(nm[1]);
      if (val >= 1 && val <= 120) age = val;
    }
  }

  // Gender
  let gender = '';
  if (
    /\bwid\w{1,4}\b|विधवा|vidhwa|महिला|औरत|स्त्री|लड़की|बेटी|\bmahila\b|\baurat\b|\bauraton\b|\bladki\b|\bkanya\b|female|woman|girl|widow|pregnant|गर्भवती|she\b|\bnurse\b|\banganwadi\b|\basha\s+worker\b/i.test(text)
    || FEMALE_NATIVE.some(t => text.includes(t))
  ) {
    gender = 'female';
  } else if (
    /पुरुष|आदमी|किसान|\bladka\b|\bpurush\b|\bmale\b|\bman\b|\bboy\b|\bfarmer\b|\bhe\b/i.test(text)
    || MALE_NATIVE.some(t => text.includes(t))
  ) {
    gender = 'male';
  }

  // State
  const state = detectState(text);

  // Caste
  const caste = detectCaste(text);

  // Income
  let income = 0;
  const croreM = text.match(CRORE_ALL_RE);
  if (croreM) {
    income = Math.round(parseFloat(croreM[1]) * 10_000_000);
  }
  const lakhM = !croreM && text.match(/(\d+(?:\.\d+)?)\s*(?:lakh|लाख|lac)/i);
  if (lakhM) {
    income = Math.round(parseFloat(lakhM[1]) * 100_000);
  } else {
    // "ek lakh", "do lakh" → word-form lakhs
    const wordLakhM = text.match(HINDI_LAKH_RE);
    if (wordLakhM) {
      income = (HINDI_NUM_MAP[wordLakhM[1].toLowerCase()] ?? 0) * 100_000;
    } else {
      const hazarM = text.match(/(\d+(?:\.\d+)?)\s*(?:हज़ार|हजार|hazaar|hazar|hajar|thousand|\bk\b)/i);
      if (hazarM) {
        income = Math.round(parseFloat(hazarM[1]) * 1_000);
      } else {
        // "paanch hazaar", "das hazar" → word-form thousands
        const wordHazaarM = text.match(HINDI_HAZAAR_RE);
        if (wordHazaarM) {
          income = (HINDI_NUM_MAP[wordHazaarM[1].toLowerCase()] ?? 0) * 1_000;
        } else {
          // Native-script lakh: "3 লক্ষ", "2 లక్ష", "5 லட்சம்"
          const nativeLakhM = text.match(LAKH_NATIVE_RE);
          if (nativeLakhM) {
            income = Math.round(parseFloat(nativeLakhM[1]) * 100_000);
          } else {
            // Native-script hazaar: "50 হাজার", "20 ஆயிரம்"
            const nativeHazaarM = text.match(HAZAAR_NATIVE_RE);
            if (nativeHazaarM) {
              income = Math.round(parseFloat(nativeHazaarM[1]) * 1_000);
            } else {
              const bareM = text.match(/(?:income|আয়|salary|வருமானம்|వేతనం|आय|वेतन)\s*[:\-]?\s*(\d{4,7})/i);
              if (bareM) income = parseInt(bareM[1]);
            }
          }
        }
      }
    }
  }

  // Flags
  const flags = detectFlags(text);
  if (flags.includes('widow') || flags.includes('pregnant')) gender = 'female';

  // Bare number fallback for age
  if (age === null) {
    const otherSignals = [gender, state, caste, income > 0, flags.length > 0].filter(Boolean).length;
    if (otherSignals >= 1) {
      const bareM = text.match(/(?<!\d)(\d{1,3})(?!\d)/);
      if (bareM) {
        const val = parseInt(bareM[1]);
        if (val >= 5 && val <= 100) age = val;
      }
    }
  }

  // Need at least 2 signals
  const count = [age, gender, state, caste, income > 0, flags.length > 0].filter(Boolean).length;
  if (count < 2) return null;

  return { age, gender, state: state ?? 'All', caste: caste ?? '', income, flags };
}
