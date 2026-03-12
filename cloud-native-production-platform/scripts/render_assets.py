from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
out_dir = ROOT / "docs" / "screenshots"
out_dir.mkdir(parents=True, exist_ok=True)


def draw_box(draw, xy, title, subtitle):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=18, fill="#0f172a", outline="#334155", width=3)
    draw.text((x1 + 18, y1 + 20), title, fill="#e2e8f0")
    draw.text((x1 + 18, y1 + 54), subtitle, fill="#94a3b8")


def make_architecture():
    img = Image.new("RGB", (1400, 900), "#020617")
    draw = ImageDraw.Draw(img)
    draw.text((50, 30), "Cloud-Native Production Platform", fill="#ffffff")
    draw.text((50, 65), "AWS target architecture overview", fill="#94a3b8")
    draw_box(draw, (60, 140, 280, 250), "Route 53", "DNS entrypoint")
    draw_box(draw, (360, 140, 610, 250), "ALB", "health checks and routing")
    draw_box(draw, (700, 100, 1000, 270), "ECS Gateway", "public API service")
    draw_box(draw, (1120, 140, 1330, 250), "CloudWatch", "logs and alarms")
    draw_box(draw, (540, 430, 760, 540), "Catalog", "stateless service")
    draw_box(draw, (860, 430, 1080, 540), "Orders", "stateful service")
    draw_box(draw, (850, 670, 1160, 800), "RDS PostgreSQL", "managed persistence")
    draw_box(draw, (140, 430, 390, 540), "Frontend", "static UI")
    draw.line((280, 195, 360, 195), fill="#60a5fa", width=5)
    draw.line((610, 195, 700, 195), fill="#60a5fa", width=5)
    draw.line((1000, 195, 1120, 195), fill="#60a5fa", width=5)
    draw.line((850, 270, 650, 430), fill="#60a5fa", width=5)
    draw.line((850, 270, 970, 430), fill="#60a5fa", width=5)
    draw.line((970, 540, 1010, 670), fill="#60a5fa", width=5)
    img.save(out_dir / "architecture-overview.png")


def make_local_stack():
    img = Image.new("RGB", (1400, 900), "#0f172a")
    draw = ImageDraw.Draw(img)
    draw.text((50, 35), "Local Docker Compose Stack", fill="#ffffff")
    draw.text((50, 70), "frontend, gateway, catalog, orders, Prometheus, and Grafana", fill="#94a3b8")
    boxes = [
        ((70, 180, 320, 310), "frontend:8080", "Nginx static UI"),
        ((380, 180, 630, 310), "gateway:8000", "public API + aggregation"),
        ((690, 180, 940, 310), "catalog:8001", "inventory API"),
        ((1000, 180, 1250, 310), "orders:8002", "SQLite-backed orders"),
        ((380, 430, 630, 560), "prometheus:9090", "metrics scrape"),
        ((690, 430, 940, 560), "grafana:3000", "dashboards"),
    ]
    for spec in boxes:
        draw_box(draw, *spec)
    draw.line((320, 245, 380, 245), fill="#60a5fa", width=5)
    draw.line((630, 245, 690, 245), fill="#60a5fa", width=5)
    draw.line((630, 245, 1000, 245), fill="#60a5fa", width=5)
    draw.line((505, 310, 505, 430), fill="#60a5fa", width=5)
    draw.line((815, 310, 815, 430), fill="#60a5fa", width=5)
    img.save(out_dir / "local-stack.png")


def make_metrics():
    img = Image.new("RGB", (1400, 900), "#111827")
    draw = ImageDraw.Draw(img)
    draw.text((50, 35), "Metrics Overview", fill="#ffffff")
    draw.text((50, 70), "Example dashboard snapshot for request rate and latency", fill="#94a3b8")
    draw.rounded_rectangle((60, 130, 420, 350), radius=18, fill="#0f172a", outline="#334155", width=3)
    draw.text((90, 170), "Gateway req/s", fill="#e2e8f0")
    draw.text((90, 230), "127.4", fill="#38bdf8")
    draw.rounded_rectangle((490, 130, 850, 350), radius=18, fill="#0f172a", outline="#334155", width=3)
    draw.text((520, 170), "Orders req/s", fill="#e2e8f0")
    draw.text((520, 230), "41.8", fill="#38bdf8")
    draw.rounded_rectangle((920, 130, 1280, 350), radius=18, fill="#0f172a", outline="#334155", width=3)
    draw.text((950, 170), "Gateway p95 latency", fill="#e2e8f0")
    draw.text((950, 230), "142 ms", fill="#38bdf8")
    draw.rounded_rectangle((60, 430, 1280, 780), radius=18, fill="#0f172a", outline="#334155", width=3)
    draw.line((110, 700, 250, 640, 390, 615, 530, 560, 670, 520, 810, 470, 950, 430, 1090, 380, 1230, 340), fill="#60a5fa", width=6)
    draw.text((90, 455), "Gateway latency trend", fill="#e2e8f0")
    img.save(out_dir / "metrics-overview.png")


if __name__ == "__main__":
    make_architecture()
    make_local_stack()
    make_metrics()
    print(f"Rendered screenshots into {out_dir}")
