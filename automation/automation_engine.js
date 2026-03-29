/**
 * htmlfonts.com Flat-File Automation Engine
 * Version: 1.8 (Auto-Discovery Mode)
 */

const fs = require('fs');
const path = require('path');

const DATA_PATH = path.resolve(__dirname, '../frontend/src/data.json'); 

const FONT_LIST = [
  { id: 'inter', family: 'Inter' },
  { id: 'syne', family: 'Syne' },
  { id: 'fraunces', family: 'Fraunces' },
  { id: 'roboto', family: 'Roboto' },
  { id: 'lora', family: 'Lora' },
  { id: 'montserrat', family: 'Montserrat' },
  { id: 'playfair-display', family: 'Playfair Display' }
];

async function getAvailableModel(apiKey) {
  console.log("🔍 Finding a supported model for your API key...");
  const listUrl = `https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`;
  
  try {
    const res = await fetch(listUrl);
    const data = await res.json();
    
    if (data.error) throw new Error(data.error.message);

    // Look for a 'flash' model that supports content generation
    const bestModel = data.models.find(m => 
      m.supportedGenerationMethods.includes("generateContent") && 
      m.name.includes("flash")
    );

    if (bestModel) {
      console.log(`🎯 Found compatible model: ${bestModel.name}`);
      return bestModel.name; // This will look like "models/gemini-1.5-flash"
    }
    
    // Fallback to the first available model if no flash is found
    return data.models[0].name;
  } catch (e) {
    console.error("❌ Could not list models. Defaulting to gemini-1.5-flash.");
    return "models/gemini-1.5-flash";
  }
}

async function generateAIContent(prompt, systemInstruction) {
  const apiKey = process.env.GEMINI_API_KEY; 
  if (!apiKey || apiKey === "undefined") throw new Error("GEMINI_API_KEY missing.");

  // STEP 1: Discover which model your account actually supports
  const modelName = await getAvailableModel(apiKey);
  const url = `https://generativelanguage.googleapis.com/v1beta/${modelName}:generateContent?key=${apiKey}`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{
          parts: [{ text: `INSTRUCTION: ${systemInstruction}\n\nTASK: ${prompt}` }]
        }]
      })
    });
    
    const result = await response.json();
    if (result.error) throw new Error(result.error.message);

    return result.candidates?.[0]?.content?.parts?.[0]?.text;
  } catch (e) {
    throw new Error(`API Request Failed: ${e.message}`);
  }
}

async function runAutomation() {
  console.log("🚀 Starting daily typography engine...");

  const dir = path.dirname(DATA_PATH);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

  const h = FONT_LIST[Math.floor(Math.random() * FONT_LIST.length)];
  const b = FONT_LIST[Math.floor(FONT_LIST.indexOf(h) === 0 ? 1 : 0)];

  const seoPrompt = `Write a 400-word SEO article for "Pairing ${h.family} and ${b.family}". Format as JSON: {"title": "...", "slug": "...", "meta_description": "...", "content_body": "..."}`;
  const system = "You are a Typography and SEO expert. Output raw JSON only. No markdown.";

  try {
    console.log(`📡 Fetching analysis for ${h.family} + ${b.family}...`);
    const rawResponse = await generateAIContent(seoPrompt, system);
    
    const jsonMatch = rawResponse.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error("No valid JSON found.");

    const newArticle = JSON.parse(jsonMatch[0]);
    newArticle.date = new Date().toISOString();
    newArticle.fonts = [h.family, b.family];

    let database = [];
    if (fs.existsSync(DATA_PATH)) {
      const content = fs.readFileSync(DATA_PATH, 'utf8');
      try { database = JSON.parse(content || "[]"); } catch (e) { database = []; }
    }

    database.unshift(newArticle);
    fs.writeFileSync(DATA_PATH, JSON.stringify(database, null, 2));
    
    console.log(`✅ Success! Generated: ${newArticle.title}`);

  } catch (err) {
    console.error("❌ Process Failed:", err.message);
    process.exit(1);
  }
}

runAutomation();
