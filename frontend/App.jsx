import articles from './src/data.json';
import React, { useState, useEffect, useMemo } from 'react';
import { 
  Type, Copy, Shuffle, Monitor, Layout, 
  Moon, Sun, ChevronDown, Check, Search, Filter, 
  Zap, Star, Download, CreditCard, Share2, ArrowRight,
  BookOpen, Code, Trophy
} from 'lucide-react';

// The ultimate font library for the engine
const FONT_LIBRARY = [
  { id: 'inter', family: 'Inter', category: 'Sans Serif', weight: '400,700,900' },
  { id: 'roboto', family: 'Roboto', category: 'Sans Serif', weight: '400,700,900' },
  { id: 'playfair-display', family: 'Playfair Display', category: 'Serif', weight: '400,700,900' },
  { id: 'syne', family: 'Syne', category: 'Display', weight: '400,700,800' },
  { id: 'montserrat', family: 'Montserrat', category: 'Sans Serif', weight: '400,700,900' },
  { id: 'lora', family: 'Lora', category: 'Serif', weight: '400,700' },
  { id: 'fira-code', family: 'Fira Code', category: 'Monospace', weight: '400,700' },
  { id: 'poppins', family: 'Poppins', category: 'Sans Serif', weight: '400,700,900' },
  { id: 'merriweather', family: 'Merriweather', category: 'Serif', weight: '400,700,900' },
  { id: 'space-grotesk', family: 'Space Grotesk', category: 'Sans Serif', weight: '400,700' },
  { id: 'dm-sans', family: 'DM Sans', category: 'Sans Serif', weight: '400,700' },
];

const SEO_ARTICLES = [
  { slug: 'inter-vs-roboto-best-saas-font', title: 'Inter vs Roboto: The Ultimate SaaS Font Showdown', fonts: ['Inter', 'Roboto'], readTime: '4 min' },
  { slug: 'playfair-and-montserrat-pairing', title: 'Why Playfair Display & Montserrat is the Golden Rule', fonts: ['Playfair Display', 'Montserrat'], readTime: '5 min' },
  { slug: 'syne-font-modern-ui', title: 'Using Syne for High-Impact Display Typography', fonts: ['Syne', 'Inter'], readTime: '3 min' }
];

export default function App() {
  const [headingFont, setHeadingFont] = useState(FONT_LIBRARY[3]);
  const [bodyFont, setBodyFont] = useState(FONT_LIBRARY[0]);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [activeTab, setActiveTab] = useState('preview');
  const [copied, setCopied] = useState(false);
  const [showPaywall, setShowPaywall] = useState(false);

  useEffect(() => {
    const link = document.createElement('link');
    const fonts = [headingFont, bodyFont].map(f => `${f.family.replace(/\s+/g, '+')}:wght@${f.weight}`).join('&family=');
    link.href = `https://fonts.googleapis.com/css2?family=${fonts}&display=swap`;
    link.rel = 'stylesheet';
    document.head.appendChild(link);
    return () => { if (document.head.contains(link)) document.head.removeChild(link); };
  }, [headingFont, bodyFont]);

  const handleCopyCSS = () => {
    const css = `/* htmlfonts.com production typography */\n:root {\n  --font-heading: '${headingFont.family}', sans-serif;\n  --font-body: '${bodyFont.family}', sans-serif;\n}\n\nh1, h2, h3 {\n  font-family: var(--font-heading);\n  font-weight: 800;\n}\n\nbody {\n  font-family: var(--font-body);\n  line-height: 1.6;\n}`;
    document.execCommand('copy'); 
    const textArea = document.createElement("textarea");
    textArea.value = css;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand("copy");
    document.body.removeChild(textArea);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const FontSelector = ({ label, current, onSelect }) => (
    <div className="flex flex-col gap-2">
      <label className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400 dark:text-slate-500">{label}</label>
      <div className="relative">
        <select 
          value={current.id}
          onChange={(e) => onSelect(FONT_LIBRARY.find(f => f.id === e.target.value))}
          className="w-full appearance-none bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50 rounded-2xl px-4 py-4 pr-10 text-sm focus:ring-2 focus:ring-blue-500 outline-none transition-all cursor-pointer font-medium text-slate-900 dark:text-white"
        >
          {['Sans Serif', 'Serif', 'Display', 'Monospace'].map(cat => (
            <optgroup label={cat} key={cat}>
              {FONT_LIBRARY.filter(f => f.category === cat).map(font => (
                <option key={font.id} value={font.id}>{font.family}</option>
              ))}
            </optgroup>
          ))}
        </select>
        <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
      </div>
    </div>
  );

  return (
    <div className={`min-h-screen flex flex-col transition-colors duration-500 ${isDarkMode ? 'dark bg-[#0B0F19] text-slate-100' : 'bg-slate-50 text-slate-900'}`}>
      <header className="border-b border-slate-200/50 dark:border-white/5 bg-white/80 dark:bg-[#0B0F19]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-[1400px] mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-tr from-blue-600 to-indigo-500 p-2 rounded-xl shadow-lg shadow-blue-500/20">
              <Type className="text-white w-5 h-5" />
            </div>
            <span className="font-extrabold text-2xl tracking-tight">htmlfonts<span className="text-blue-500">.com</span></span>
          </div>
          <div className="flex items-center gap-4">
            <button onClick={() => setIsDarkMode(!isDarkMode)} className="p-3 rounded-xl bg-slate-100 dark:bg-white/5 transition-colors">
              {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            <button onClick={() => setShowPaywall(true)} className="bg-blue-600 text-white px-6 py-3 rounded-xl text-sm font-bold shadow-xl hover:scale-105 transition-all">
              Go Pro
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 w-full flex flex-col items-center">
        <section className="w-full max-w-[1400px] mx-auto px-6 py-20 text-center relative">
          <h1 className="text-5xl md:text-8xl font-black tracking-tighter leading-[1.05] mb-8" style={{ fontFamily: headingFont.family }}>
            Typography <span className="text-blue-500">Redefined</span>.
          </h1>
          <p className="text-lg md:text-2xl text-slate-600 dark:text-slate-400 max-w-3xl leading-relaxed mx-auto" style={{ fontFamily: bodyFont.family }}>
            Test your favorite pairings in real-time and export production-ready CSS with one click.
          </p>
        </section>

        <section id="lab" className="w-full max-w-[1400px] mx-auto px-6 py-10 z-10">
          <div className="flex flex-col lg:flex-row gap-8">
            <aside className="w-full lg:w-96 flex flex-col gap-6">
              <div className="bg-white dark:bg-[#131A2B] border border-slate-200/50 dark:border-white/5 rounded-[2rem] p-8 shadow-2xl">
                <h2 className="font-bold text-xl mb-8 flex items-center gap-3">
                  <Layout className="w-5 h-5 text-blue-500" /> Pairing Lab
                </h2>
                <div className="space-y-8">
                  <FontSelector label="Heading Font" current={headingFont} onSelect={setHeadingFont} />
                  <FontSelector label="Body Font" current={bodyFont} onSelect={setBodyFont} />
                  <button 
                    onClick={handleCopyCSS}
                    className={`w-full py-4 rounded-2xl font-bold text-lg transition-all shadow-xl ${
                      copied ? 'bg-emerald-500 text-white' : 'bg-blue-600 text-white hover:shadow-blue-500/40'
                    }`}
                  >
                    {copied ? 'Copied!' : 'Export CSS'}
                  </button>
                </div>
              </div>
            </aside>

            <div className="flex-1 bg-white dark:bg-[#131A2B] border border-slate-200/50 dark:border-white/5 rounded-[2.5rem] p-8 md:p-16 shadow-2xl min-h-[600px]">
              <div className="max-w-2xl mx-auto">
                <h2 className="text-5xl md:text-7xl font-extrabold leading-[1.1] mb-8" style={{ fontFamily: headingFont.family }}>
                  Design with <span className="italic text-slate-400">confidence</span>.
                </h2>
                <p className="text-xl text-slate-600 dark:text-slate-400 leading-[1.8] mb-12" style={{ fontFamily: bodyFont.family }}>
                  HTMLFonts helps you discover font pairings that satisfy both aesthetic taste and technical performance. Clean typography is the fastest way to improve your website's conversion rate.
                </p>
                <button className="px-10 py-5 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-2xl font-bold text-lg" style={{ fontFamily: bodyFont.family }}>
                  Start Free Trial
                </button>
              </div>
            </div>
          </div>
        </section>

        <section id="articles" className="w-full max-w-[1400px] mx-auto px-6 py-24 border-t border-slate-200/50 dark:border-white/5 mt-12">
          <h2 className="text-4xl font-black mb-12 flex items-center gap-3">
            <BookOpen className="w-8 h-8 text-blue-500" /> Daily AI Guides
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {SEO_ARTICLES.map((article, i) => (
              <a key={i} href={`/review/${article.slug}`} className="p-8 rounded-[2rem] bg-white dark:bg-[#131A2B] border border-slate-200/50 dark:border-white/5 hover:border-blue-500/50 transition-colors">
                <h3 className="text-2xl font-bold mb-4">{article.title}</h3>
                <span className="text-blue-500 font-bold flex items-center gap-1">Read Analysis <ArrowRight className="w-4 h-4" /></span>
              </a>
            ))}
          </div>
        </section>
      </main>

      {showPaywall && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-md" onClick={() => setShowPaywall(false)}></div>
          <div className="relative bg-white dark:bg-[#131A2B] w-full max-w-lg rounded-[2.5rem] p-10 shadow-2xl border dark:border-white/10 text-center">
            <Zap className="w-16 h-16 text-amber-500 mx-auto mb-6 fill-current" />
            <h2 className="text-3xl font-black mb-4">Go Pro</h2>
            <p className="text-slate-500 mb-8">Unlock API access and custom font uploads.</p>
            <button className="w-full py-5 bg-blue-600 text-white rounded-2xl font-black text-lg">Subscribe • $15/mo</button>
          </div>
        </div>
      )}
    </div>
  );
}
