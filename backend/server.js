const express = require('express');
const { createClient } = require('@supabase/supabase-js');
const helmet = require('helmet');

const app = express();
const PORT = process.env.PORT || 3000;

const supabase = createClient(
  process.env.SUPABASE_URL || 'https://your-project.supabase.co',
  process.env.SUPABASE_ANON_KEY || 'your-anon-key'
);

app.use(helmet({ contentSecurityPolicy: false })); // Permissive for font testing

/**
 * SSR ROUTE: Programmatic SEO Pages
 * Serves the AI-generated reviews to crawlers.
 */
app.get('/review/:slug', async (req, res) => {
  const { slug } = req.params;

  try {
    const { data: article, error } = await supabase
      .from('seo_pages')
      .select('*')
      .eq('slug', slug)
      .single();

    if (error || !article) {
      return res.status(404).send('<h1>Typography Guide Not Found</h1>');
    }

    const html = `
      <!DOCTYPE html>
      <html lang="en">
      <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>${article.title} | htmlfonts.com</title>
          <meta name="description" content="${article.meta_description}">
          <style>
            body { font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; line-height: 1.6; color: #333; }
            h1 { font-size: 2.5rem; letter-spacing: -0.02em; }
            .badge { background: #e0f2fe; color: #0369a1; padding: 5px 12px; rounded: 20px; font-weight: bold; font-size: 0.8rem; }
          </style>
      </head>
      <body>
          <nav><a href="/">← htmlfonts.com Lab</a></nav>
          <article>
            <span class="badge">AI-Generated Analysis</span>
            <h1>${article.title}</h1>
            <main>${article.content_body}</main>
          </article>
      </body>
      </html>
    `;

    res.setHeader('Content-Type', 'text/html');
    res.status(200).send(html);
  } catch (err) {
    res.status(500).send('Server Error');
  }
});

app.listen(PORT, () => {
  console.log(`SEO Server active on ${PORT}`);
});
