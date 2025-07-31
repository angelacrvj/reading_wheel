import streamlit.components.v1 as components
import json

def roue_interactive(livres, lancer=False, height=600):
    html_code = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
      <meta charset="UTF-8">
      <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.11.0/gsap.min.js"></script>
      <script src="https://cdn.jsdelivr.net/gh/zarocknz/javascript-winwheel@master/Winwheel.min.js"></script>
    </head>
    <body style="margin:0; display:flex; justify-content:center; align-items:center; height:{height}px;">
      <canvas id="canvas" width="550" height="550"></canvas>
      <script>
        let roue;
        const livres = {json.dumps(livres)};
        
        if (livres && livres.length > 0) {{
          const couleurs = ['#e74c3c', '#f1c40f', '#2ecc71', '#3498db', '#9b59b6', '#e67e22'];
          const segments = livres.map((titre, i) => {{
            // Tronquer les titres trop longs
            let texteAffiche = titre;
            if (titre.length > 45) {{
                texteAffiche = titre.substring(0, 40) + "...";
            }}
            
            return {{
                fillStyle: couleurs[i % couleurs.length],
                text: texteAffiche,
                textFillStyle: '#ffffff',
                textFontSize: Math.max(10, Math.min(16, 200 / livres.length))
            }};
           }});

        

        roue = new Winwheel({{
        canvasId: 'canvas',
        numSegments: segments.length,
        segments: segments,
        textAlignment: 'center',
        textOrientation: 'horizontal',
        textMargin: 5,
        animation: {{
            type: 'spinToStop',
            duration: 3,
            spins: 4 + Math.random() * 2,
            callbackFinished: function (segment) {{
            console.log("🎯 Livre sélectionné :", segment.text);
            window.parent.postMessage({{
                type: "streamlit:setComponentValue",
                value: segment.text
            }}, "*");
            }}
        }}
        }});

          if ({json.dumps(lancer)}) {{
            setTimeout(() => roue.startAnimation(), 200);
          }}
        }}
      </script>
    </body>
    </html>
    """
    return components.html(html_code, height=height)