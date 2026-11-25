"""Gera os SVGs do README do perfil (estética 8 bits anos 80 + cyberpunk).

As fontes pixel vão embutidas em base64: o GitHub bloqueia fontes externas em imagens.
Uso:  python3 tools/build.py      (escreve em assets/)
"""
import base64
import html
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
FONTS = ROOT / "tools" / "fonts"
W = 840

# Paleta synthwave
BG0, BG1 = "#0b0221", "#2a0b4a"
PINK, CYAN, YELLOW, ORANGE, PURPLE = "#ff2a6d", "#05d9e8", "#f9c80e", "#ff6c11", "#b14aed"
WHITE, DIM, PANEL = "#f5e9ff", "#9d8cc8", "#140531"


def font_face(name: str, file: str) -> str:
    data = base64.b64encode((FONTS / file).read_bytes()).decode()
    return f"@font-face{{font-family:'{name}';src:url(data:font/woff2;base64,{data}) format('woff2');}}"


STYLE = f"""<style>
{font_face('PS2P', 'press-start-2p.woff2')}
{font_face('VT', 'vt323.woff2')}
.px{{font-family:'PS2P',monospace}}
.vt{{font-family:'VT',monospace}}
</style>"""

DEFS = f"""<defs>
  <filter id="glow" x="-20%" y="-50%" width="140%" height="200%">
    <feGaussianBlur stdDeviation="3" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="soft" x="-10%" y="-30%" width="120%" height="160%">
    <feGaussianBlur stdDeviation="1.6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
    <rect width="4" height="2" fill="#000" opacity="0.28"/>
  </pattern>
  <linearGradient id="panel" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{PANEL}"/><stop offset="1" stop-color="{BG0}"/>
  </linearGradient>
</defs>"""


def svg(h: int, body: str, title: str) -> str:
    title = html.escape(title)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" '
            f'role="img" aria-label="{title}"><title>{title}</title>{STYLE}{DEFS}{body}'
            f'<rect width="{W}" height="{h}" fill="url(#scan)" pointer-events="none"/></svg>')


def pixel_frame(x: int, y: int, w: int, h: int, color: str, accent: str) -> str:
    """Moldura de jogo 8 bits: borda dupla com cantos 'mordidos' em degrau."""
    s = 4  # tamanho do pixel
    outer = (f"M{x + 2 * s},{y} H{x + w - 2 * s} V{y + s} H{x + w - s} V{y + 2 * s} H{x + w} V{y + h - 2 * s} "
             f"H{x + w - s} V{y + h - s} H{x + w - 2 * s} V{y + h} H{x + 2 * s} V{y + h - s} H{x + s} "
             f"V{y + h - 2 * s} H{x} V{y + 2 * s} H{x + s} V{y + s} H{x + 2 * s} Z")
    return (f'<path d="{outer}" fill="url(#panel)" stroke="{color}" stroke-width="2" filter="url(#soft)"/>'
            f'<path d="{outer}" fill="none" stroke="{accent}" stroke-width="1" opacity="0.5" '
            f'transform="translate(3 3)"/>')


def tag(x: int, y: int, text: str, color: str, size: int = 10) -> str:
    """Etiqueta de seção estilo HUD: bloco colorido + texto pixel."""
    w = len(text) * size + 20
    return (f'<rect x="{x}" y="{y - size - 7}" width="{w}" height="{size + 12}" fill="{color}"/>'
            f'<text class="px" x="{x + 10}" y="{y}" font-size="{size}" fill="{BG0}">{text}</text>')


def cursor(x: float, y: float, color: str, w: int = 10, h: int = 12, dur: str = "1s") -> str:
    return f'<rect x="{x}" y="{y - h}" width="{w}" height="{h}" fill="{color}">{blink(dur)}</rect>'


def blink(dur: str = "1s") -> str:
    return f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="{dur}" repeatCount="indefinite"/>'


# ---------------------------------------------------------------- hero
def hero() -> str:
    H, horizon = 320, 214
    rnd = random.Random(1985)
    stars = []
    for i in range(70):
        x, y, s = rnd.randrange(W), rnd.randrange(horizon - 20), rnd.choice((2, 2, 2, 3))
        tw = (f'<animate attributeName="opacity" values="1;0.2;1" dur="{rnd.uniform(1.5, 4):.1f}s" '
              f'begin="{rnd.uniform(0, 3):.1f}s" repeatCount="indefinite"/>' if i % 4 == 0 else "")
        stars.append(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="{WHITE}" opacity="{rnd.uniform(0.35, 0.9):.2f}">{tw}</rect>')

    # sol com faixas (máscara), atrás do horizonte
    cx, cy, r = 724, horizon - 6, 84
    bands = "".join(
        f'<rect x="{cx - r}" y="{cy - 30 + i * 13}" width="{2 * r}" height="{2 + i * 1.6:.1f}" fill="#000"/>'
        for i in range(8))
    sun = f"""
    <linearGradient id="sun" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{YELLOW}"/><stop offset="0.55" stop-color="{ORANGE}"/><stop offset="1" stop-color="{PINK}"/>
    </linearGradient>
    <mask id="sunmask"><rect x="0" y="0" width="{W}" height="{horizon}" fill="#fff"/>{bands}</mask>
    <circle cx="{cx}" cy="{cy}" r="{r + 26}" fill="{PINK}" opacity="0.18" filter="url(#glow)"/>
    <circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#sun)" mask="url(#sunmask)"/>"""

    # montanhas em pixel (silhueta)
    mx, pts = 0, [f"0,{horizon}"]
    rnd2 = random.Random(7)
    while mx < W:
        mx += rnd2.randrange(28, 70)
        pts.append(f"{mx},{horizon - rnd2.randrange(10, 46)}")
    pts.append(f"{W},{horizon}")
    mountains = f'<polygon points="{" ".join(pts)}" fill="#1a0636" stroke="{PURPLE}" stroke-width="1.2" opacity="0.95"/>'

    # chão em grade com perspectiva; as linhas horizontais "andam" na direção de quem olha
    vx = W / 2
    verticals = "".join(
        f'<line x1="{vx + (i * 26)}" y1="{horizon}" x2="{vx + i * 150}" y2="{H}"/>' for i in range(-14, 15))
    horiz = "".join(f'<line x1="0" x2="{W}" y1="{horizon + (H - horizon) * (k / 10) ** 2:.1f}" y2="{horizon + (H - horizon) * (k / 10) ** 2:.1f}"/>'
                    for k in range(1, 11))
    floor = f"""
    <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2a0b4a"/><stop offset="1" stop-color="#0b0221"/>
    </linearGradient>
    <rect x="0" y="{horizon}" width="{W}" height="{H - horizon}" fill="url(#floor)"/>
    <g stroke="{PINK}" stroke-width="1.2" opacity="0.75" filter="url(#soft)">
      {verticals}
      <g>{horiz}<animateTransform attributeName="transform" type="translate" values="0 0;0 10" dur="1.2s" repeatCount="indefinite"/></g>
    </g>
    <rect x="0" y="{horizon - 1}" width="{W}" height="3" fill="{CYAN}" filter="url(#glow)" opacity="0.9"/>"""

    # nome com aberração cromática + subtítulo que se digita
    title = "GABTERM"
    sub = "&gt; backend · automation · systems that hold"
    sub_len = 44
    char_w = 10  # avanço do VT323 a 26 px
    steps = sub_len + 1
    typing_frac = 0.55  # digita em 55% do ciclo, depois segura o texto pronto
    dur = 9
    widths = ";".join(str(k * char_w + 6) for k in range(steps)) + f";{sub_len * char_w + 6}"
    xs = ";".join(str(44 + k * char_w) for k in range(steps)) + f";{44 + sub_len * char_w}"
    times = ";".join(f"{typing_frac * k / sub_len:.4f}" for k in range(steps)) + ";1"
    name = f"""
    <text class="px" x="46" y="112" font-size="54" fill="{CYAN}" opacity="0.75">{title}</text>
    <text class="px" x="40" y="108" font-size="54" fill="{PINK}" opacity="0.75">{title}</text>
    <text class="px" x="43" y="110" font-size="54" fill="{WHITE}" filter="url(#glow)">{title}</text>
    <text class="px" x="44" y="146" font-size="11" fill="{YELLOW}" letter-spacing="1">ELIXIR SOFTWARE ENGINEER · AI ENTHUSIAST</text>
    <clipPath id="typing"><rect x="40" y="160" height="40" width="0">
      <animate attributeName="width" values="{widths}" keyTimes="{times}" dur="{dur}s" calcMode="discrete" repeatCount="indefinite"/>
    </rect></clipPath>
    <text class="vt" x="44" y="186" font-size="26" fill="{CYAN}" clip-path="url(#typing)">{sub}</text>
    <rect x="44" y="166" width="11" height="22" fill="{PINK}">
      <animate attributeName="x" values="{xs}" keyTimes="{times}" dur="{dur}s" calcMode="discrete" repeatCount="indefinite"/>
      {blink("0.8s")}
    </rect>"""

    body = (f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG0}"/>'
            f'<stop offset="1" stop-color="{BG1}"/></linearGradient>'
            f'<rect width="{W}" height="{horizon}" fill="url(#sky)"/>{"".join(stars)}{sun}{mountains}{floor}{name}')
    return svg(H, body, "gabterm — backend · automation · systems that hold")


# ---------------------------------------------------------------- player 1
def player() -> str:
    H = 234
    # rótulos em inglês, como nos fliperamas (a Press Start 2P não tem acentos); valores em VT323
    rows = [("CLASS", "Backend Engineer", CYAN), ("SPECIAL", "Focus &amp; Flow", PINK),
            ("QUEST", "Sistemas que aguentam produção", YELLOW)]
    lines = "".join(
        f'<text class="px" x="40" y="{82 + i * 30}" font-size="10" fill="{DIM}">{k}</text>'
        f'<text class="vt" x="150" y="{84 + i * 30}" font-size="26" fill="{c}">{v}</text>'
        for i, (k, v, c) in enumerate(rows))

    def bar(y: int, label: str, color: str) -> str:
        cells = "".join(f'<rect x="{560 + i * 18}" y="{y - 12}" width="14" height="14" fill="{color}"/>' for i in range(12))
        return (f'<text class="px" x="476" y="{y}" font-size="10" fill="{DIM}">{label}</text>{cells}'
                f'<text class="px" x="{560 + 12 * 18 + 8}" y="{y}" font-size="9" fill="{color}">MAX</text>')

    items = ["ELIXIR", "PHOENIX", "PYTHON", "JS", "NODE", "ELECTRON", "LINUX"]
    colors = [PURPLE, ORANGE, YELLOW, YELLOW, CYAN, CYAN, PINK]
    x, slots = 40, []
    for it, c in zip(items, colors):
        w = len(it) * 9 + 18
        slots.append(f'<rect x="{x}" y="186" width="{w}" height="26" fill="{BG0}" stroke="{c}" stroke-width="2"/>'
                     f'<text class="px" x="{x + 9}" y="204" font-size="9" fill="{c}">{it}</text>')
        x += w + 8
    body = (f'<rect width="{W}" height="{H}" fill="{BG0}"/>{pixel_frame(12, 22, W - 28, H - 32, CYAN, PINK)}'
            f'{tag(28, 30, "PLAYER 1", CYAN)}'
            f'<text class="px" x="{W - 160}" y="30" font-size="10" fill="{YELLOW}">READY</text>{cursor(W - 104, 30, YELLOW, 9, 10, "1.2s")}'
            f'{lines}{bar(84, "FOCUS", CYAN)}{bar(114, "FLOW", PINK)}'
            f'<text class="px" x="40" y="174" font-size="9" fill="{DIM}">INVENTORY</text>{"".join(slots)}')
    return svg(H, body, "Player 1: Backend Engineer, Focus & Flow, inventário Elixir, Phoenix, Python, JS, Node, Electron, Linux")


# ---------------------------------------------------------------- main quest
def quest() -> str:
    H = 236
    goals = [(True, "Painéis ao vivo de CPU, memória, rede e arquivos"), (True, "Sandbox, sem telemetria, leve na máquina"),
             (True, "Temas, sons sintetizados e animações"), (False, "Interface em inglês"),
             (False, "Gerenciador de processos")]
    g = "".join(
        f'<rect x="40" y="{126 + i * 20}" width="12" height="12" fill="{CYAN if done else "none"}" stroke="{CYAN}" stroke-width="2"/>'
        f'<text class="vt" x="62" y="{137 + i * 20}" font-size="21" fill="{WHITE if done else DIM}">{t}</text>'
        for i, (done, t) in enumerate(goals))
    body = (f'<rect width="{W}" height="{H}" fill="{BG0}"/>{pixel_frame(12, 22, W - 28, H - 32, PINK, CYAN)}'
            f'{tag(28, 30, "MAIN QUEST", PINK)}'
            f'<text class="px" x="40" y="80" font-size="26" fill="{WHITE}" filter="url(#soft)">NEXUS</text>'
            f'<text class="px" x="190" y="80" font-size="20" fill="{CYAN}">❯<tspan>_{blink()}</tspan></text>'
            f'<text class="vt" x="40" y="108" font-size="24" fill="{DIM}">Terminal sci-fi para Linux: seu shell de verdade cercado de painéis ao vivo.</text>'
            f'{g}'
            f'<text class="px" x="{W - 290}" y="{H - 26}" font-size="10" fill="{YELLOW}">▶ PRESS START<tspan>{blink("1.4s")}_</tspan></text>'
            f'<text class="vt" x="{W - 290}" y="{H - 44}" font-size="22" fill="{CYAN}">github.com/gabterm/nexus</text>')
    return svg(H, body, "Main quest: NEXUS, terminal sci-fi para Linux")


# ---------------------------------------------------------------- side quests (só o cabeçalho)
def side() -> str:
    H = 64
    body = (f'<rect width="{W}" height="{H}" fill="{BG0}"/>{tag(16, 40, "SIDE QUESTS", YELLOW, 12)}'
            f'<line x1="200" y1="34" x2="{W - 16}" y2="34" stroke="{YELLOW}" stroke-width="2" stroke-dasharray="6 6" opacity="0.7"/>')
    return svg(H, body, "Side quests")


# ---------------------------------------------------------------- codex (axiomas)
def codex() -> str:
    axioms = [
        ("Complexidade que não ganhou o direito de existir", "não existe. — ou não deveria."),
        ("Código legado tem contexto que nenhum comentário", "vai capturar. Leia com respeito."),
        ("Solução elegante é a que você não percebe que precisava", "até ela parar de funcionar. — ou seja, nunca."),
        ("A maioria dos devs resolve o problema pedido.", "Prefiro entender qual deveria ter sido pedido."),
    ]
    roman = ["I", "II", "III", "IV"]
    colors = [PINK, CYAN, YELLOW, PURPLE]
    H = 70 + len(axioms) * 62
    rows = ""
    for i, ((a, b), n, c) in enumerate(zip(axioms, roman, colors)):
        y = 62 + i * 62
        rows += (f'<rect x="40" y="{y}" width="44" height="44" fill="{BG0}" stroke="{c}" stroke-width="2"/>'
                 f'<text class="px" x="62" y="{y + 28}" font-size="12" fill="{c}" text-anchor="middle">{n}</text>'
                 f'<text class="vt" x="100" y="{y + 18}" font-size="23" fill="{WHITE}">{a}</text>'
                 f'<text class="vt" x="100" y="{y + 40}" font-size="23" fill="{DIM}">{b}</text>')
    body = (f'<rect width="{W}" height="{H}" fill="{BG0}"/>{pixel_frame(12, 22, W - 28, H - 32, PURPLE, PINK)}'
            f'{tag(28, 30, "CODEX // AXIOMAS DE ENGENHARIA", PURPLE)}{rows}')
    return svg(H, body, "Codex: axiomas de engenharia")


# ---------------------------------------------------------------- next level
def next_level() -> str:
    H = 150
    body = (f'<rect width="{W}" height="{H}" fill="{BG0}"/>'
            f'{tag(16, 34, "NEXT LEVEL", CYAN)}'
            f'<text class="vt" x="20" y="74" font-size="25" fill="{WHITE}">Backend, IA aplicada e sistemas distribuídos —</text>'
            f'<text class="vt" x="20" y="100" font-size="25" fill="{DIM}">coisas que têm consequências reais quando dão errado.</text>'
            f'<text class="px" x="20" y="136" font-size="11" fill="{PINK}" filter="url(#soft)">INSERT COIN TO CONTINUE</text>{cursor(20 + 24 * 11, 136, PINK, 10, 11, "0.9s")}'
            f'<text class="px" x="{W - 120}" y="136" font-size="9" fill="{DIM}">CREDIT 01</text>')
    return svg(H, body, "Next level: backend, IA aplicada e sistemas distribuídos")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    # no perfil vão só o hero e o NEXUS; os outros cartões ficam aqui caso um dia queira usar
    for name, fn in [("hero", hero), ("quest", quest)]:
        (OUT / f"{name}.svg").write_text(fn(), encoding="utf-8")
        print(f"assets/{name}.svg", round((OUT / f"{name}.svg").stat().st_size / 1024), "KB")
