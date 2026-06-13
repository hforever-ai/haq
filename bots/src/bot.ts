/**
 * Aarambha Haq — Telegram Bot (TypeScript / Telegraf)
 * Free scheme eligibility checker for Indian users.
 */
import 'dotenv/config';
import { Telegraf, Markup } from 'telegraf';
import { parseProfile, initParser, normalizeState, Profile } from './parser';

// ── Config ────────────────────────────────────────────────────────────────────
const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN ?? '';
const API_BASE  = process.env.HAQ_API_URL ?? 'http://localhost:8097';
const GROQ_KEY  = process.env.GROQ_KEY ?? '';
const GROQ_BASE = 'https://api.groq.com/openai/v1/chat/completions';
const GROQ_MODELS = [
  'llama-3.1-8b-instant',
  'llama-3.3-70b-versatile',
  'meta-llama/llama-4-scout-17b-16e-instruct',
];

// ── Static data ───────────────────────────────────────────────────────────────
const LANG_OPTIONS = [
  ['hi', 'हिन्दी'], ['en', 'English'], ['mr', 'मराठी'],
  ['bn', 'বাংলা'],  ['te', 'తెలుగు'],  ['ta', 'தமிழ்'],
  ['gu', 'ગુજરાતી'],['kn', 'ಕನ್ನಡ'],   ['pa', 'ਪੰਜਾਬੀ'],
  ['ml', 'മലയാളം'], ['or', 'ଓଡ଼ିଆ'],
] as const;

const UI: Record<string, Record<string, string>> = {
  hi: {
    welcome:      '🇮🇳 *Aarambha Haq में आपका स्वागत है!*\n\nसरकारी योजनाओं की मुफ्त जानकारी — आपकी भाषा में।\n\nपहले अपनी भाषा चुनें:',
    menu:         'आप क्या करना चाहते हैं?',
    check_lbl:    '✅ पात्रता जांचें',
    search_lbl:   '🔍 योजना खोजें',
    rights_lbl:   '⚖️ अपने अधिकार',
    lang_lbl:     '🌐 भाषा बदलें',
    ask_state:    '📍 आपका राज्य क्या है?\n\nराज्य का नाम टाइप करें (जैसे: UP, Bihar, Maharashtra)',
    ask_age:      '🎂 आपकी उम्र क्या है?\n\nसिर्फ नंबर लिखें (जैसे: 35)',
    ask_gender:   '👤 आप कौन हैं?',
    female:       '👩 महिला',
    male:         '👨 पुरुष',
    other:        '🧑 अन्य',
    ask_caste:    '📋 आपकी श्रेणी क्या है?',
    ask_income:   '💰 परिवार की सालाना आय?',
    ask_flags:    'अन्य जानकारी (जो लागू हो वो सब चुनें, फिर ✅ Done दबाएं):',
    done_flags:   '✅ Done',
    searching:    '🔍 आपके लिए योजनाएं खोज रहे हैं...',
    results_hdr:  '🎯 *आपके लिए {n} योजनाएं मिलीं!*\n',
    no_results:   '😔 आपकी जानकारी से कोई योजना नहीं मिली।\nफ़िल्टर बदलें या वेबसाइट पर देखें:\nhaq.aarambhax.in',
    search_prompt:'योजना का नाम या विषय टाइप करें\n(जैसे: scholarship, छात्रवृत्ति, kisan, महिला)',
    rights_hdr:   '⚖️ *आपके अधिकार*\n\nश्रेणी चुनें:',
    invalid_age:  '⚠️ कृपया सही उम्र डालें (1-120)',
    website_link: '🌐 पूरी वेबसाइट: haq.aarambhax.in',
  },
  en: {
    welcome:      '🇮🇳 *Welcome to Aarambha Haq!*\n\nFree government scheme finder in your language.\n\nChoose your language:',
    menu:         'What would you like to do?',
    check_lbl:    '✅ Check Eligibility',
    search_lbl:   '🔍 Search Schemes',
    rights_lbl:   '⚖️ Know Your Rights',
    lang_lbl:     '🌐 Change Language',
    ask_state:    '📍 What is your state?\n\nType the state name (e.g. UP, Bihar, Maharashtra)',
    ask_age:      '🎂 What is your age?\n\nType a number (e.g. 35)',
    ask_gender:   '👤 Who are you?',
    female:       '👩 Female',
    male:         '👨 Male',
    other:        '🧑 Other',
    ask_caste:    '📋 What is your category?',
    ask_income:   '💰 Annual family income?',
    ask_flags:    'Any of the following apply? (select all, then press ✅ Done):',
    done_flags:   '✅ Done',
    searching:    '🔍 Finding schemes for you...',
    results_hdr:  '🎯 *Found {n} schemes for you!*\n',
    no_results:   '😔 No schemes found for your profile.\nTry changing filters or visit:\nhaq.aarambhax.in',
    search_prompt:'Type a scheme name or topic\n(e.g. scholarship, kisan, housing, mahila)',
    rights_hdr:   '⚖️ *Your Rights*\n\nChoose a category:',
    invalid_age:  '⚠️ Please enter a valid age (1-120)',
    website_link: '🌐 Full website: haq.aarambhax.in',
  },
};

const INCOME_OPTIONS: Record<string, [string, number][]> = {
  hi: [['0–1 लाख', 80000], ['1–3 लाख', 200000], ['3–6 लाख', 450000], ['6–10 लाख', 800000], ['10+ लाख', 1500000]],
  en: [['0–1 Lakh', 80000], ['1–3 Lakh', 200000], ['3–6 Lakh', 450000], ['6–10 Lakh', 800000], ['10+ Lakh', 1500000]],
};

const CASTE_OPTIONS: Record<string, [string, string][]> = {
  hi: [['SC', 'SC'], ['ST', 'ST'], ['OBC', 'OBC'], ['EWS', 'EWS'], ['General/सामान्य', 'General']],
  en: [['SC', 'SC'], ['ST', 'ST'], ['OBC', 'OBC'], ['EWS', 'EWS'], ['General', 'General']],
};

const FLAG_OPTIONS: Record<string, [string, string][]> = {
  hi: [['विधवा', 'widow'], ['दिव्यांग', 'disability'], ['अल्पसंख्यक', 'minority'], ['BPL कार्ड', 'bpl'], ['गर्भवती', 'pregnant']],
  en: [['Widow', 'widow'], ['Disabled', 'disability'], ['Minority', 'minority'], ['BPL Card', 'bpl'], ['Pregnant', 'pregnant']],
};

const RIGHTS_CATEGORIES: Record<string, [string, string][]> = {
  hi: [
    ['mahila-haq', '👩 महिला हक'], ['gharelu-hinsa', '🛡️ घरेलू हिंसा'],
    ['prasuti', '🤱 प्रसूति'],      ['talak', '⚖️ तलाक'],
    ['sampatti', '🏠 संपत्ति'],     ['pension', '👴 पेंशन'],
    ['legal-aid', '🧑‍⚖️ कानूनी सहायता'], ['shiksha-rozgar', '📚 शिक्षा/रोज़गार'],
  ],
  en: [
    ['mahila-haq', '👩 Women\'s Rights'], ['gharelu-hinsa', '🛡️ Domestic Violence'],
    ['prasuti', '🤱 Maternity'],           ['talak', '⚖️ Divorce/Family'],
    ['sampatti', '🏠 Property'],           ['pension', '👴 Pension'],
    ['legal-aid', '🧑‍⚖️ Legal Aid'],        ['shiksha-rozgar', '📚 Education/Employment'],
  ],
};

// ── LLM prompts ───────────────────────────────────────────────────────────────
const PROFILE_PROMPT = `You extract a user's personal profile from free-text messages in Hindi, English, or Hinglish.
OUTPUT: Return ONLY a single JSON object.
{"age":<int|null>,"gender":<"male"|"female"|"other"|null>,"state":<full Indian state name|null>,"caste":<"SC"|"ST"|"OBC"|"EWS"|"General"|null>,"income":<annual INR int|null>,"flags":<[] or subset of ["widow","disability","minority","bpl","pregnant"]>}
RULES:
1. Explicit caste wins — "SC tribe" → caste="SC".
2. Typo states: "rajsthan"→"Rajasthan", "jharkand"→"Jharkhand".
3. Widow variants: "vidwa","vidhwa","widoe" → flags=["widow"], gender="female".
4. Income: "1.5 lakh"→150000, "50k"→50000.
5. If NOT a profile, return all nulls.
EXAMPLES:
"मैं 45 साल की विधवा हूं UP से BPL है" → {"age":45,"gender":"female","state":"Uttar Pradesh","caste":null,"income":null,"flags":["widow","bpl"]}
"35 year old SC Bihar farmer" → {"age":35,"gender":"male","state":"Bihar","caste":"SC","income":null,"flags":[]}
"disability pension 60 saal kerala" → {"age":60,"gender":null,"state":"Kerala","caste":null,"income":null,"flags":["disability"]}
"घर बनाने के लिए पैसे चाहिए" → {"age":null,"gender":null,"state":null,"caste":null,"income":null,"flags":[]}`;

const SEARCH_PROMPT = `Convert an Indian user's query about government schemes into 2-3 English search keywords.
Return ONLY the keywords — no explanation.
"घर बनाने के लिए पैसे" → "housing construction"
"बेटी की पढ़ाई के लिए" → "girl education scholarship"
"बुजुर्ग पेंशन" → "old age pension"
"दिव्यांग भत्ता" → "disability allowance"`;

const FOLLOWUP_PROMPTS: Record<string, string> = {
  hi: 'आप Saavi हैं — Aarambha Haq के सहायक। दी गई योजनाओं के बारे में यूजर के सवाल का 2-4 वाक्यों में हिंदी में जवाब दें।',
  en: 'You are Saavi, assistant for Aarambha Haq. Answer the user\'s question in 2-4 sentences in English based only on the scheme data provided.',
  mr: 'तुम्ही Saavi आहात — Aarambha Haq चे सहाय्यक. मराठीत 2-4 वाक्यांत उत्तर द्या.',
  bn: 'আপনি Saavi — Aarambha Haq-এর সহকারী। বাংলায় 2-4 বাক্যে উত্তর দিন।',
  te: 'మీరు Saavi — Aarambha Haq సహాయకుడు. తెలుగులో 2-4 వాక్యాలలో సమాధానం ఇవ్వండి.',
  ta: 'நீங்கள் Saavi — Aarambha Haq உதவியாளர். தமிழில் 2-4 வாக்யங்களில் பதில் சொல்லுங்கள்.',
  gu: 'તમે Saavi છો — Aarambha Haq ના સહાયક. ગુજરાતીમાં 2-4 વાક્યોમાં જવાબ આપો.',
  kn: 'ನೀವು Saavi — Aarambha Haq ಸಹಾಯಕ. ಕನ್ನಡದಲ್ಲಿ 2-4 ವಾಕ್ಯಗಳಲ್ಲಿ ಉತ್ತರಿಸಿ.',
  pa: 'ਤੁਸੀਂ Saavi ਹੋ — Aarambha Haq ਦੇ ਸਹਾਇਕ. ਪੰਜਾਬੀ ਵਿੱਚ 2-4 ਵਾਕਾਂ ਵਿੱਚ ਜਵਾਬ ਦਿਓ.',
  ml: 'നിങ്ങൾ Saavi ആണ് — Aarambha Haq സഹായി. മലയാളത്തിൽ 2-4 വാക്യങ്ങളിൽ ഉത്തരം നൽകുക.',
};

// ── Groq LLM (waterfall: llama-3.1-8b → 70b → llama-4) ──────────────────────
async function llmCall(prompt: string, system = '', jsonMode = false): Promise<string | null> {
  if (!GROQ_KEY) return null;
  const messages = [];
  if (system) messages.push({ role: 'system', content: system });
  messages.push({ role: 'user', content: prompt });
  const body: Record<string, unknown> = { messages, max_tokens: 512 };
  if (jsonMode) body.response_format = { type: 'json_object' };

  for (const model of GROQ_MODELS) {
    try {
      const res = await fetch(GROQ_BASE, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${GROQ_KEY}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...body, model }),
        signal: AbortSignal.timeout(12_000),
      });
      if (res.ok) {
        const data = await res.json() as { choices: { message: { content: string } }[] };
        return data.choices[0].message.content;
      }
      if (res.status !== 429) break; // non-rate-limit error — stop waterfall
    } catch { /* timeout / network — try next model */ }
  }
  return null;
}

async function smartParseProfile(text: string): Promise<Profile | null> {
  if (text.split(/\s+/).length < 3) return null;

  const ruleResult = parseProfile(text);
  if (ruleResult) return ruleResult;

  if (!GROQ_KEY) return null;
  const hints = ['साल','year','उम्र','age','विधवा','widow','BPL','SC','ST','OBC','female','state','हूं','income','आय'];
  if (!hints.some(h => text.toLowerCase().includes(h.toLowerCase()))) return null;

  const raw = await llmCall(text, PROFILE_PROMPT, true);
  if (!raw) return null;
  try {
    const p = JSON.parse(raw);
    if (!p.age && !p.gender && !p.state && !p.caste && !p.income && !p.flags?.length) return null;
    return {
      age:    p.age ? parseInt(p.age) : null,
      gender: p.gender ?? '',
      state:  p.state ?? 'All',
      caste:  p.caste ?? '',
      income: p.income ? parseInt(p.income) : 0,
      flags:  p.flags ?? [],
    };
  } catch { return null; }
}

async function smartSearchKeywords(query: string): Promise<string> {
  const raw = await llmCall(`User query: ${query}`, SEARCH_PROMPT);
  return raw && raw.trim().length < 60 ? raw.trim() : query;
}

async function smartFollowup(question: string, schemes: Scheme[], lang: string): Promise<string | null> {
  if (!schemes.length) return null;
  const context = schemes.slice(0, 5).map(s => {
    const amt = s.benefit_amount_inr ? `₹${s.benefit_amount_inr.toLocaleString('en-IN')}` : (s.benefit_amount_description ?? '');
    return `- ${s.name}: ${(s.description ?? '').slice(0, 100)} | Benefit: ${amt}`;
  }).join('\n');
  const system = FOLLOWUP_PROMPTS[lang] ?? FOLLOWUP_PROMPTS['en'];
  const raw = await llmCall(`Schemes:\n${context}\n\nUser question: ${question}`, system);
  return raw?.trim() ?? null;
}

// ── API helpers ───────────────────────────────────────────────────────────────
interface TgUser {
  lang: string;
  step: string;
  profile: Profile | null;
  results: Scheme[] | null;
  first_name: string;
  username: string;
}

interface Scheme {
  name: string;
  level: string;
  state: string;
  benefit_type?: string;
  benefit_amount_inr?: number;
  benefit_amount_description?: string;
  apply_url?: string;
  description?: string;
}

interface Article { title_hi: string; summary_hi: string; category: string; }

async function getUser(chatId: number): Promise<TgUser> {
  try {
    const res = await fetch(`${API_BASE}/api/bot/user/${chatId}`, { signal: AbortSignal.timeout(5_000) });
    return res.ok ? (await res.json() as TgUser) : ({} as TgUser);
  } catch { return {} as TgUser; }
}

async function saveUser(chatId: number, updates: Record<string, unknown>): Promise<void> {
  try {
    await fetch(`${API_BASE}/api/bot/user/${chatId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
      signal: AbortSignal.timeout(5_000),
    });
  } catch { /* non-critical */ }
}

async function getLang(chatId: number): Promise<string> {
  const u = await getUser(chatId);
  return u.lang ?? 'hi';
}

async function apiCheck(profile: Profile): Promise<Scheme[]> {
  try {
    const p = new URLSearchParams({
      gender: profile.gender ?? '',
      age: String(profile.age ?? 30),
      state: profile.state ?? 'All',
      income: String(profile.income ?? 0),
      caste: profile.caste ?? '',
      has_disability: profile.flags.includes('disability') ? '1' : '0',
      is_minority:    profile.flags.includes('minority')   ? '1' : '0',
      has_bpl:        profile.flags.includes('bpl')        ? '1' : '0',
    });
    const res = await fetch(`${API_BASE}/api/check/results?${p}`, { signal: AbortSignal.timeout(10_000) });
    return res.ok ? ((await res.json() as { schemes: Scheme[] }).schemes ?? []) : [];
  } catch { return []; }
}

async function apiSearch(q: string): Promise<Scheme[]> {
  try {
    const res = await fetch(`${API_BASE}/api/schemes?q=${encodeURIComponent(q)}&size=8&page=1`, { signal: AbortSignal.timeout(10_000) });
    return res.ok ? ((await res.json() as { schemes: Scheme[] }).schemes ?? []) : [];
  } catch { return []; }
}

async function apiRights(category = ''): Promise<Article[]> {
  try {
    const q = category ? `?category=${category}` : '';
    const res = await fetch(`${API_BASE}/api/rights${q}`, { signal: AbortSignal.timeout(10_000) });
    return res.ok ? ((await res.json() as { articles: Article[] }).articles ?? []) : [];
  } catch { return []; }
}

// ── UI helpers ────────────────────────────────────────────────────────────────
function ui(lang: string, key: string, vars?: Record<string, string | number>): string {
  const dict = UI[lang] ?? UI['hi'];
  let text = dict[key] ?? UI['hi'][key] ?? key;
  if (vars) Object.entries(vars).forEach(([k, v]) => { text = text.replace(`{${k}}`, String(v)); });
  return text;
}

function menuKb(lang: string) {
  return Markup.inlineKeyboard([
    [Markup.button.callback(ui(lang, 'check_lbl'),  'menu:check')],
    [Markup.button.callback(ui(lang, 'search_lbl'), 'menu:search')],
    [Markup.button.callback(ui(lang, 'rights_lbl'), 'menu:rights')],
    [Markup.button.callback(ui(lang, 'lang_lbl'),   'menu:lang')],
  ]);
}

function langKb() {
  const rows: ReturnType<typeof Markup.button.callback>[][] = [];
  let row: ReturnType<typeof Markup.button.callback>[] = [];
  for (const [code, label] of LANG_OPTIONS) {
    row.push(Markup.button.callback(label, `lang:${code}`));
    if (row.length === 3) { rows.push(row); row = []; }
  }
  if (row.length) rows.push(row);
  return Markup.inlineKeyboard(rows);
}

function genderKb(lang: string) {
  return Markup.inlineKeyboard([[
    Markup.button.callback(ui(lang, 'female'), 'gender:female'),
    Markup.button.callback(ui(lang, 'male'),   'gender:male'),
    Markup.button.callback(ui(lang, 'other'),  'gender:other'),
  ]]);
}

function casteKb(lang: string) {
  const opts = CASTE_OPTIONS[lang] ?? CASTE_OPTIONS['hi'];
  return Markup.inlineKeyboard(opts.map(([label, val]) => [Markup.button.callback(label, `caste:${val}`)]));
}

function incomeKb(lang: string) {
  const opts = INCOME_OPTIONS[lang] ?? INCOME_OPTIONS['hi'];
  return Markup.inlineKeyboard(opts.map(([label, val]) => [Markup.button.callback(label, `income:${val}`)]));
}

function flagsKb(lang: string, selected: string[]) {
  const opts = FLAG_OPTIONS[lang] ?? FLAG_OPTIONS['hi'];
  const rows = opts.map(([label, val]) => [
    Markup.button.callback((selected.includes(val) ? '✅ ' : '☐ ') + label, `flag:${val}`),
  ]);
  rows.push([Markup.button.callback(ui(lang, 'done_flags'), 'flag:done')]);
  return Markup.inlineKeyboard(rows);
}

function rightsKb(lang: string) {
  const opts = RIGHTS_CATEGORIES[lang] ?? RIGHTS_CATEGORIES['hi'];
  const rows = opts.map(([slug, label]) => [Markup.button.callback(label, `rights:${slug}`)]);
  rows.push([Markup.button.callback('⬅️ Menu', 'menu:back')]);
  return Markup.inlineKeyboard(rows);
}

function applyKb(schemes: Scheme[], offset = 0) {
  const rows = schemes
    .map((s, i) => s.apply_url ? [Markup.button.url(`📋 ${i + 1 + offset}. आवेदन करें`, s.apply_url)] : null)
    .filter((r): r is ReturnType<typeof Markup.button.url>[] => r !== null);
  return rows.length ? Markup.inlineKeyboard(rows) : null;
}

function fmtScheme(s: Scheme, idx: number): string {
  const flag  = s.level === 'Central' ? '🏛' : '🗺';
  const name  = (s.name ?? '').slice(0, 60);
  const state = s.state && s.state !== 'All' ? ` • ${s.state}` : '';
  let benefit = '';
  if (s.benefit_amount_inr) {
    benefit = s.benefit_amount_inr >= 100_000
      ? `\n  💰 ₹${(s.benefit_amount_inr / 100_000).toFixed(1)} लाख`
      : `\n  💰 ₹${s.benefit_amount_inr.toLocaleString('en-IN')}`;
  } else if (s.benefit_amount_description) {
    benefit = `\n  💰 ${s.benefit_amount_description.slice(0, 50)}`;
  }
  return `${idx}. ${flag} *${name}*${state}${benefit}`;
}

// ── Bot setup ─────────────────────────────────────────────────────────────────
const bot = new Telegraf(BOT_TOKEN);

// /start
bot.command('start', async (ctx) => {
  const chatId = ctx.chat.id;
  await saveUser(chatId, { step: 'idle', first_name: ctx.from?.first_name ?? '', username: ctx.from?.username ?? '' });
  await ctx.reply(UI['hi']['welcome'], { parse_mode: 'Markdown', reply_markup: langKb().reply_markup });
});

// /menu
bot.command('menu', async (ctx) => {
  const chatId = ctx.chat.id;
  const lang   = await getLang(chatId);
  await saveUser(chatId, { step: 'idle' });
  await ctx.reply(ui(lang, 'menu'), { reply_markup: menuKb(lang).reply_markup });
});

// /check
bot.command('check', async (ctx) => {
  const chatId = ctx.chat.id;
  const lang   = await getLang(chatId);
  await saveUser(chatId, { step: 'ask_state', profile: null });
  await ctx.reply(ui(lang, 'ask_state'));
});

// /search
bot.command('search', async (ctx) => {
  const chatId = ctx.chat.id;
  const lang   = await getLang(chatId);
  await saveUser(chatId, { step: 'search' });
  await ctx.reply(ui(lang, 'search_prompt'));
});

// /haq
bot.command('haq', async (ctx) => {
  const chatId = ctx.chat.id;
  const lang   = await getLang(chatId);
  await ctx.reply(ui(lang, 'rights_hdr'), { parse_mode: 'Markdown', reply_markup: rightsKb(lang).reply_markup });
});

// ── Callback actions ──────────────────────────────────────────────────────────
bot.action(/^lang:(.+)$/, async (ctx) => {
  await ctx.answerCbQuery();
  const chatId  = ctx.chat!.id;
  const newLang = ctx.match[1];
  await saveUser(chatId, { lang: newLang, step: 'idle' });
  await ctx.editMessageText(ui(newLang, 'menu'), { reply_markup: menuKb(newLang).reply_markup });
});

bot.action('menu:lang', async (ctx) => {
  await ctx.answerCbQuery();
  const lang = await getLang(ctx.chat!.id);
  await ctx.editMessageText(ui(lang, 'welcome'), { parse_mode: 'Markdown', reply_markup: langKb().reply_markup });
});

bot.action('menu:check', async (ctx) => {
  await ctx.answerCbQuery();
  const chatId = ctx.chat!.id;
  const lang   = await getLang(chatId);
  await saveUser(chatId, { step: 'ask_state', profile: null });
  await ctx.editMessageText(ui(lang, 'ask_state'));
});

bot.action('menu:search', async (ctx) => {
  await ctx.answerCbQuery();
  const chatId = ctx.chat!.id;
  const lang   = await getLang(chatId);
  await saveUser(chatId, { step: 'search' });
  await ctx.editMessageText(ui(lang, 'search_prompt'));
});

bot.action(/^menu:(rights|back)$/, async (ctx) => {
  await ctx.answerCbQuery();
  const chatId = ctx.chat!.id;
  const lang   = await getLang(chatId);
  await ctx.editMessageText(ui(lang, 'rights_hdr'), { parse_mode: 'Markdown', reply_markup: rightsKb(lang).reply_markup });
});

bot.action(/^gender:(.+)$/, async (ctx) => {
  await ctx.answerCbQuery();
  const chatId = ctx.chat!.id;
  const lang   = await getLang(chatId);
  const user   = await getUser(chatId);
  const profile = { ...(user.profile ?? {}), gender: ctx.match[1] };
  await saveUser(chatId, { step: 'ask_caste', profile });
  await ctx.editMessageText(ui(lang, 'ask_caste'), { reply_markup: casteKb(lang).reply_markup });
});

bot.action(/^caste:(.+)$/, async (ctx) => {
  await ctx.answerCbQuery();
  const chatId = ctx.chat!.id;
  const lang   = await getLang(chatId);
  const user   = await getUser(chatId);
  const profile = { ...(user.profile ?? {}), caste: ctx.match[1] };
  await saveUser(chatId, { step: 'ask_income', profile });
  await ctx.editMessageText(ui(lang, 'ask_income'), { reply_markup: incomeKb(lang).reply_markup });
});

bot.action(/^income:(\d+)$/, async (ctx) => {
  await ctx.answerCbQuery();
  const chatId  = ctx.chat!.id;
  const lang    = await getLang(chatId);
  const user    = await getUser(chatId);
  const profile = { ...(user.profile ?? {}), income: parseInt(ctx.match[1]), flags: (user.profile as Profile)?.flags ?? [] };
  await saveUser(chatId, { step: 'ask_flags', profile });
  await ctx.editMessageText(ui(lang, 'ask_flags'), { reply_markup: flagsKb(lang, profile.flags as string[]).reply_markup });
});

bot.action(/^flag:(.+)$/, async (ctx) => {
  await ctx.answerCbQuery();
  const chatId  = ctx.chat!.id;
  const lang    = await getLang(chatId);
  const user    = await getUser(chatId);
  const profile = { ...(user.profile ?? {}) } as Profile;
  profile.flags = [...((profile.flags ?? []) as string[])];
  const flagVal = ctx.match[1];

  if (flagVal === 'done') {
    await saveUser(chatId, { step: 'idle' });
    await ctx.editMessageText(ui(lang, 'searching'));
    const schemes = await apiCheck(profile);
    if (!schemes.length) {
      await ctx.editMessageText(ui(lang, 'no_results'), { reply_markup: menuKb(lang).reply_markup });
    } else {
      const shown = schemes.slice(0, 7);
      const lines = [ui(lang, 'results_hdr', { n: schemes.length }), ...shown.map((s, i) => fmtScheme(s, i + 1))];
      const kb = applyKb(shown);
      await ctx.editMessageText(lines.join('\n'), { parse_mode: 'Markdown' });
      if (kb) await ctx.reply(ui(lang, 'website_link'), { reply_markup: kb.reply_markup });
      await ctx.reply(ui(lang, 'menu'), { reply_markup: menuKb(lang).reply_markup });
    }
  } else {
    const idx = profile.flags.indexOf(flagVal);
    if (idx >= 0) profile.flags.splice(idx, 1);
    else profile.flags.push(flagVal);
    await saveUser(chatId, { profile });
    await ctx.editMessageText(ui(lang, 'ask_flags'), { reply_markup: flagsKb(lang, profile.flags).reply_markup });
  }
});

bot.action(/^rights:(.+)$/, async (ctx) => {
  await ctx.answerCbQuery();
  const chatId   = ctx.chat!.id;
  const lang     = await getLang(chatId);
  const category = ctx.match[1];
  const articles = await apiRights(category);
  if (!articles.length) { await ctx.editMessageText('कोई अधिकार नहीं मिला।'); return; }

  const catMap = Object.fromEntries((RIGHTS_CATEGORIES[lang] ?? RIGHTS_CATEGORIES['hi']));
  const header = `*${catMap[category] ?? 'अधिकार'}*\n\n`;
  const lines  = articles.slice(0, 6).map(a => `• *${a.title_hi}*\n  ${a.summary_hi.slice(0, 120)}...\n`);
  await ctx.editMessageText(header + lines.join('\n') + '\n🌐 haq.aarambhax.in/hi/haq', {
    parse_mode: 'Markdown',
    reply_markup: rightsKb(lang).reply_markup,
  });
});

// ── Text message handler ──────────────────────────────────────────────────────
bot.on('text', async (ctx) => {
  const chatId = ctx.chat.id;
  const text   = ctx.message.text.trim();
  const lang   = await getLang(chatId);
  const user   = await getUser(chatId);
  const step   = user.step ?? 'idle';

  if (step === 'ask_state') {
    const profile = { state: normalizeState(text) };
    await saveUser(chatId, { step: 'ask_age', profile });
    await ctx.reply(ui(lang, 'ask_age'));

  } else if (step === 'ask_age') {
    const n = parseInt(text);
    if (!/^\d{1,3}$/.test(text) || n < 1 || n > 120) {
      await ctx.reply(ui(lang, 'invalid_age')); return;
    }
    const profile = { ...(user.profile ?? {}), age: n };
    await saveUser(chatId, { step: 'ask_gender', profile });
    await ctx.reply(ui(lang, 'ask_gender'), { reply_markup: genderKb(lang).reply_markup });

  } else if (step === 'search') {
    await saveUser(chatId, { step: 'idle' });
    let query = text;
    if (text.split(/\s+/).length > 3 && GROQ_KEY) {
      await ctx.reply(lang === 'hi' ? '🔍 समझ रहे हैं...' : '🔍 Analyzing...');
      const better = await smartSearchKeywords(text);
      if (better !== text) query = better;
    }
    let schemes = await apiSearch(query);
    if (!schemes.length && query !== text) schemes = await apiSearch(text);
    if (!schemes.length) {
      await ctx.reply(lang === 'hi' ? `'${text}' के लिए कोई योजना नहीं मिली।` : `No schemes found for '${text}'.`);
      return;
    }
    const shown = schemes.slice(0, 6);
    const lines = [lang === 'hi' ? `🔍 *${schemes.length} योजनाएं मिलीं*\n` : `🔍 *${schemes.length} schemes found*\n`,
                   ...shown.map((s, i) => fmtScheme(s, i + 1))];
    await saveUser(chatId, { results: shown, step: 'awaiting_followup' });
    const kb = applyKb(shown);
    await ctx.reply(lines.join('\n'), { parse_mode: 'Markdown', ...(kb ? { reply_markup: kb.reply_markup } : {}) });
    await ctx.reply(
      lang === 'hi' ? '💬 कोई सवाल पूछें — \'इसमें कितना मिलेगा?\' या \'कैसे apply करें?\'' : '💬 Ask a follow-up — \'How much money?\' or \'How to apply?\'',
      { reply_markup: menuKb(lang).reply_markup },
    );

  } else if (step === 'awaiting_followup') {
    const schemes = (user.results ?? []) as Scheme[];
    await saveUser(chatId, { step: 'idle' });
    const thinking = await ctx.reply(lang === 'hi' ? '🤔 सोच रहे हैं...' : '🤔 Thinking...');
    const answer   = GROQ_KEY ? await smartFollowup(text, schemes, lang) : null;
    await ctx.telegram.deleteMessage(chatId, thinking.message_id).catch(() => null);
    await ctx.reply(
      answer ?? (lang === 'hi' ? 'माफ़ करें, अभी जवाब नहीं दे पा रहे। वेबसाइट पर देखें: haq.aarambhax.in' : 'Sorry, can\'t answer right now. Visit: haq.aarambhax.in'),
      { reply_markup: menuKb(lang).reply_markup },
    );

  } else if (step === 'idle' && text.split(/\s+/).length >= 3) {
    const thinking = await ctx.reply(lang === 'hi' ? '🤖 समझ रहे हैं...' : '🤖 Understanding...');
    const profile  = await smartParseProfile(text);
    await ctx.telegram.deleteMessage(chatId, thinking.message_id).catch(() => null);

    if (profile) {
      const parts: string[] = [];
      if (profile.age)    parts.push(lang === 'hi' ? `• उम्र: ${profile.age} साल` : `• Age: ${profile.age}`);
      if (profile.gender) parts.push(lang === 'hi' ? `• लिंग: ${{ female: 'महिला', male: 'पुरुष', other: 'अन्य' }[profile.gender] ?? profile.gender}` : `• Gender: ${profile.gender}`);
      if (profile.state !== 'All') parts.push(lang === 'hi' ? `• राज्य: ${profile.state}` : `• State: ${profile.state}`);
      if (profile.caste)  parts.push(`• वर्ग: ${profile.caste}`);
      if (profile.income) parts.push(lang === 'hi' ? `• आय: ₹${profile.income.toLocaleString('en-IN')}/साल` : `• Income: ₹${profile.income.toLocaleString('en-IN')}/yr`);
      if (profile.flags.length) {
        const fmap: Record<string, string> = { widow: 'विधवा', disability: 'दिव्यांग', minority: 'अल्पसंख्यक', bpl: 'BPL', pregnant: 'गर्भवती' };
        parts.push((lang === 'hi' ? '• अन्य: ' : '• Flags: ') + profile.flags.map(f => lang === 'hi' ? (fmap[f] ?? f) : f).join(', '));
      }
      const confirm = (lang === 'hi' ? '✅ *समझा! आपकी जानकारी:*\n' : '✅ *Got it! Your profile:*\n')
        + parts.join('\n')
        + (lang === 'hi' ? '\n\n🔍 योजनाएं खोज रहे हैं...' : '\n\n🔍 Finding schemes...');
      await ctx.reply(confirm, { parse_mode: 'Markdown' });

      const schemes = await apiCheck(profile);
      await saveUser(chatId, { profile, results: schemes.slice(0, 7), step: schemes.length ? 'awaiting_followup' : 'idle' });

      if (!schemes.length) {
        await ctx.reply(ui(lang, 'no_results'), { reply_markup: menuKb(lang).reply_markup });
      } else {
        const shown = schemes.slice(0, 7);
        const lines = [ui(lang, 'results_hdr', { n: schemes.length }), ...shown.map((s, i) => fmtScheme(s, i + 1))];
        const kb = applyKb(shown);
        await ctx.reply(lines.join('\n'), { parse_mode: 'Markdown' });
        if (kb) await ctx.reply(ui(lang, 'website_link'), { reply_markup: kb.reply_markup });
        await ctx.reply(
          lang === 'hi' ? '💬 कोई सवाल पूछें — \'कितना मिलेगा?\' \'कैसे apply करें?\'' : '💬 Ask anything — \'How much?\' \'How to apply?\'',
          { reply_markup: menuKb(lang).reply_markup },
        );
      }
    } else {
      await ctx.reply(ui(lang, 'menu'), { reply_markup: menuKb(lang).reply_markup });
    }
  } else {
    await ctx.reply(ui(lang, 'menu'), { reply_markup: menuKb(lang).reply_markup });
  }
});

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  if (!BOT_TOKEN) {
    console.error('❌ Set TELEGRAM_BOT_TOKEN env var first.');
    process.exit(1);
  }

  console.log('⏳ Loading spell checker...');
  await initParser();
  console.log('✅ Spell checker ready.');

  bot.launch({ dropPendingUpdates: true });
  console.log('🤖 Aarambha Haq bot started. Press Ctrl+C to stop.');

  process.once('SIGINT',  () => bot.stop('SIGINT'));
  process.once('SIGTERM', () => bot.stop('SIGTERM'));
}

main().catch(console.error);
