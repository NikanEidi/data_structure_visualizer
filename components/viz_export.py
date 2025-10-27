from io import BytesIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio
from matplotlib.backends.backend_pdf import PdfPages
import os, tempfile, uuid

def _fig_to_img(fig):
    buf = BytesIO()
    FigureCanvas(fig).print_png(buf)
    img = Image.open(BytesIO(buf.getvalue())).convert("RGB")
    return img

def _caption(img, text):
    if not text:
        return img
    h = 64
    w = img.width
    footer = Image.new("RGB", (w, h), (12, 14, 20))
    draw = ImageDraw.Draw(footer)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    draw.text((16, 18), text, fill=(220, 230, 250), font=font)
    out = Image.new("RGB", (w, img.height + h), (10, 12, 18))
    out.paste(img, (0, 0))
    out.paste(footer, (0, img.height))
    return out

def export_media(simulate, render, out_basename, fmt="GIF", fps=6, simulate_kwargs=None, render_kwargs=None):
    simulate_kwargs = simulate_kwargs or {}
    render_kwargs = render_kwargs or {}
    frames = []
    descs = []
    for state, desc in simulate(**simulate_kwargs):
        fig = render(state, **render_kwargs)
        img = _fig_to_img(fig)
        frames.append(img)
        descs.append(desc)

    framed = [_caption(frames[i], descs[i]) for i in range(len(frames))]

    tmpdir = tempfile.gettempdir()
    base = f"{out_basename}_{uuid.uuid4().hex[:6]}"
    if fmt.upper() == "GIF":
        path = os.path.join(tmpdir, f"{base}.gif")
        imageio.mimsave(path, [np.array(x) for x in framed], duration=max(1/fps, 0.01), loop=0)
        return path
    if fmt.upper() == "MP4":
        path = os.path.join(tmpdir, f"{base}.mp4")
        with imageio.get_writer(path, fps=fps, codec="libx264", quality=8) as w:
            for fr in framed:
                w.append_data(np.array(fr))
        return path
    path = os.path.join(tmpdir, f"{base}.pdf")
    with PdfPages(path) as pdf:
        for fr in framed:
            buf = BytesIO()
            fr.save(buf, format="PNG")
            img = Image.open(BytesIO(buf.getvalue()))
            fig = None
            try:
                import matplotlib.pyplot as plt
                fig = plt.figure(figsize=(8.27, 11.69))
                ax = fig.add_axes([0, 0, 1, 1])
                ax.axis("off")
                ax.imshow(img)
                pdf.savefig(fig)
                plt.close(fig)
            finally:
                if fig is not None:
                    try: fig.clf()
                    except: pass
    return path