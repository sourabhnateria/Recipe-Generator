import openai
import os
from dotenv import load_dotenv

load_dotenv()
from flask import Flask, render_template_string, request

app = Flask(__name__)
client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get('OPENROUTER_API_KEY')
)

def generate_tutorial(components):
    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        max_tokens=1000,
        messages=[{
            "role": "system",
            "content": "You are a helpful assistant"
        }, {
            "role": "user",
            "content": f"Suggest a recipe using the items listed as available. Make sure you have a nice name for this recipe listed at the start. Also, include a funny version of the name of the recipe on the following line. Then share the recipe in a step-by-step manner. In the end, write a fun fact about the recipe or any of the items used in the recipe. Here are the items available: {components}, Haldi, Chilly Powder, Tomato Ketchup, Water, Garam Masala, Oil"
        }]
    )
    return response.choices[0].message.content

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Recipe Wizard</title>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg:        #0d0d0d;
      --surface:   #161616;
      --border:    #2a2a2a;
      --accent:    #e8c97e;
      --accent2:   #c0392b;
      --text:      #f0ece3;
      --muted:     #7a7570;
      --radius:    16px;
    }

    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'DM Sans', sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 60px 20px 80px;
      position: relative;
      overflow-x: hidden;
    }

    /* Ambient background blobs */
    body::before, body::after {
      content: '';
      position: fixed;
      border-radius: 50%;
      filter: blur(120px);
      opacity: 0.18;
      pointer-events: none;
      z-index: 0;
    }
    body::before {
      width: 600px; height: 600px;
      background: radial-gradient(circle, #e8c97e, transparent 70%);
      top: -150px; left: -200px;
    }
    body::after {
      width: 500px; height: 500px;
      background: radial-gradient(circle, #c0392b, transparent 70%);
      bottom: -100px; right: -150px;
    }

    .wrapper {
      position: relative;
      z-index: 1;
      width: 100%;
      max-width: 720px;
    }

    /* Header */
    header {
      text-align: center;
      margin-bottom: 52px;
    }
    .badge {
      display: inline-block;
      background: rgba(232,201,126,0.12);
      border: 1px solid rgba(232,201,126,0.3);
      color: var(--accent);
      font-size: 11px;
      letter-spacing: 2.5px;
      text-transform: uppercase;
      padding: 6px 16px;
      border-radius: 100px;
      margin-bottom: 20px;
    }
    h1 {
      font-family: 'Playfair Display', serif;
      font-size: clamp(2.4rem, 6vw, 3.6rem);
      font-weight: 700;
      line-height: 1.1;
      letter-spacing: -0.5px;
    }
    h1 em {
      font-style: italic;
      color: var(--accent);
    }
    .subtitle {
      margin-top: 14px;
      color: var(--muted);
      font-size: 15px;
      font-weight: 300;
      line-height: 1.6;
    }

    /* Card */
    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 36px;
      margin-bottom: 28px;
      transition: border-color 0.3s;
    }
    .card:focus-within {
      border-color: rgba(232,201,126,0.4);
    }

    label {
      display: block;
      font-size: 11px;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 12px;
    }

    .input-row {
      display: flex;
      gap: 12px;
    }

    input[type="text"] {
      flex: 1;
      background: rgba(255,255,255,0.04);
      border: 1px solid var(--border);
      border-radius: 10px;
      color: var(--text);
      font-family: 'DM Sans', sans-serif;
      font-size: 15px;
      padding: 14px 18px;
      outline: none;
      transition: border-color 0.25s, background 0.25s;
    }
    input[type="text"]::placeholder { color: var(--muted); }
    input[type="text"]:focus {
      border-color: var(--accent);
      background: rgba(232,201,126,0.06);
    }

    .btn-primary {
      background: var(--accent);
      color: #0d0d0d;
      border: none;
      border-radius: 10px;
      font-family: 'DM Sans', sans-serif;
      font-size: 14px;
      font-weight: 500;
      letter-spacing: 0.3px;
      padding: 14px 24px;
      cursor: pointer;
      white-space: nowrap;
      transition: background 0.2s, transform 0.15s;
    }
    .btn-primary:hover { background: #f0d898; transform: translateY(-1px); }
    .btn-primary:active { transform: translateY(0); }
    .btn-primary:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none;
    }

    /* Pantry chips */
    .pantry {
      margin-top: 20px;
      padding-top: 20px;
      border-top: 1px solid var(--border);
    }
    .pantry-label {
      font-size: 11px;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 10px;
    }
    .chips {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .chip {
      background: rgba(255,255,255,0.05);
      border: 1px solid var(--border);
      border-radius: 100px;
      color: var(--muted);
      font-size: 12px;
      padding: 4px 12px;
    }

    /* Output card */
    .output-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
      opacity: 0;
      transform: translateY(16px);
      transition: opacity 0.4s ease, transform 0.4s ease;
    }
    .output-card.visible {
      opacity: 1;
      transform: translateY(0);
    }
    .output-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 24px;
      border-bottom: 1px solid var(--border);
      background: rgba(255,255,255,0.02);
    }
    .output-title {
      font-size: 11px;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: var(--muted);
    }
    .btn-copy {
      background: transparent;
      border: 1px solid var(--border);
      border-radius: 8px;
      color: var(--muted);
      font-family: 'DM Sans', sans-serif;
      font-size: 12px;
      padding: 6px 14px;
      cursor: pointer;
      transition: border-color 0.2s, color 0.2s;
    }
    .btn-copy:hover { border-color: var(--accent); color: var(--accent); }
    .btn-copy.copied { border-color: #4caf7d; color: #4caf7d; }

    #output {
      padding: 28px 32px;
      font-size: 15px;
      line-height: 1.85;
      white-space: pre-wrap;
      color: var(--text);
      font-weight: 300;
      min-height: 80px;
    }

    /* Loading shimmer */
    .shimmer {
      display: none;
      padding: 28px 32px;
    }
    .shimmer.active { display: block; }
    .shimmer-line {
      height: 14px;
      border-radius: 6px;
      background: linear-gradient(90deg, var(--border) 25%, #2f2f2f 50%, var(--border) 75%);
      background-size: 200% 100%;
      animation: shimmer 1.4s infinite;
      margin-bottom: 12px;
    }
    .shimmer-line:nth-child(2) { width: 85%; animation-delay: 0.1s; }
    .shimmer-line:nth-child(3) { width: 70%; animation-delay: 0.2s; }
    .shimmer-line:nth-child(4) { width: 90%; animation-delay: 0.3s; }
    .shimmer-line:nth-child(5) { width: 60%; animation-delay: 0.4s; }
    @keyframes shimmer {
      0%   { background-position: 200% 0; }
      100% { background-position: -200% 0; }
    }

    /* Decorative spice icons */
    .spice-row {
      display: flex;
      justify-content: center;
      gap: 20px;
      margin-bottom: 44px;
      opacity: 0.35;
    }
    .spice-row span { font-size: 24px; }

    footer {
      margin-top: 60px;
      text-align: center;
      color: var(--muted);
      font-size: 12px;
      letter-spacing: 0.5px;
    }
  </style>
</head>
<body>
  <div class="wrapper">
    <header>
      <div class="badge">AI Recipe Wizard</div>
      <h1>Cook something<br/><em>extraordinary</em></h1>
      <p class="subtitle">Tell us what's in your kitchen.<br/>We'll conjure a recipe worth remembering.</p>
    </header>

    <div class="spice-row">
      <span>🌶</span><span>🧅</span><span>🫙</span><span>🍳</span><span>🌿</span>
    </div>

    <div class="card">
      <label for="components">Your Ingredients</label>
      <form id="tutorial-form" onsubmit="event.preventDefault(); generateTutorial();">
        <div class="input-row">
          <input
            type="text"
            id="components"
            name="components"
            placeholder="e.g. Bread, Potato, Eggs…"
            required
            autocomplete="off"
          />
          <button type="submit" class="btn-primary" id="submit-btn">
            Cook it ✦
          </button>
        </div>
      </form>
      <div class="pantry">
        <div class="pantry-label">Always in your pantry</div>
        <div class="chips">
          <span class="chip">Haldi</span>
          <span class="chip">Chilly Powder</span>
          <span class="chip">Tomato Ketchup</span>
          <span class="chip">Garam Masala</span>
          <span class="chip">Oil</span>
          <span class="chip">Water</span>
        </div>
      </div>
    </div>

    <div class="output-card" id="output-card">
      <div class="output-header">
        <span class="output-title">Your Recipe</span>
        <button class="btn-copy" id="copy-btn" onclick="copyToClipboard()">Copy</button>
      </div>
      <div class="shimmer" id="shimmer">
        <div class="shimmer-line"></div>
        <div class="shimmer-line"></div>
        <div class="shimmer-line"></div>
        <div class="shimmer-line"></div>
        <div class="shimmer-line"></div>
      </div>
      <pre id="output" style="display:none">{{ output }}</pre>
    </div>

    <footer>Made with <span>❤️</span> by Sourabh Nateria</footer>
  </div>

  <script>
    const card = document.getElementById('output-card');
    const shimmer = document.getElementById('shimmer');
    const output = document.getElementById('output');
    const submitBtn = document.getElementById('submit-btn');

    // Show pre-rendered output on page load if present
    if (output.textContent.trim()) {
      card.classList.add('visible');
      output.style.display = 'block';
    }

    async function generateTutorial() {
      const components = document.querySelector('#components').value;

      // Show card with shimmer
      card.classList.add('visible');
      shimmer.classList.add('active');
      output.style.display = 'none';
      submitBtn.disabled = true;
      submitBtn.textContent = 'Cooking…';

      try {
        const response = await fetch('/generate', {
          method: 'POST',
          body: new FormData(document.querySelector('#tutorial-form')),
        });
        const text = await response.text();
        shimmer.classList.remove('active');
        output.textContent = text;
        output.style.display = 'block';
      } catch (err) {
        shimmer.classList.remove('active');
        output.textContent = 'Something went wrong. Please try again.';
        output.style.display = 'block';
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Cook it ✦';
      }
    }

    function copyToClipboard() {
      const btn = document.getElementById('copy-btn');
      navigator.clipboard.writeText(output.textContent).then(() => {
        btn.textContent = 'Copied!';
        btn.classList.add('copied');
        setTimeout(() => {
          btn.textContent = 'Copy';
          btn.classList.remove('copied');
        }, 2000);
      });
    }
  </script>
</body>
</html>'''

@app.route('/', methods=['GET', 'POST'])
def hello():
    output = ""
    if request.method == 'POST':
        components = request.form['components']
        output = generate_tutorial(components)
    return render_template_string(HTML_TEMPLATE, output=output)

@app.route('/generate', methods=['POST'])
def generate():
    components = request.form['components']
    return generate_tutorial(components)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)