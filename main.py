import json
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, unquote_plus, urljoin, urlparse

import requests
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

URLS = [
    "https://www.enjoei.com.br/gremio/s?ref=products_search&sid=b80b88c4-f731-4fc5-ac0a-d0e9a89a2815-1760462698214&q=gremio&lp=24h&sr=same_country",
    "https://www.enjoei.com.br/1997/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=1997&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/inter/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=inter&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/corinthians/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=corinthians&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/palmeiras/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=palmeiras&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/santos/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=santos&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/sao+paulo/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=sao+paulo&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/flamengo/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=flamengo&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/vasco/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=vasco&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/fluminense/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=fluminense&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/botafogo/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=botafogo&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/cruzeiro/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=cruzeiro&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/atletico/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=atletico&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/coritiba/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=coritiba&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/independiente/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=independiente&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/boca+juniors/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=boca+juniors&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/river+plate/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=river+plate&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/san+lorenzo/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=san+lorenzo&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/barcelona/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=barcelona&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/real+madrid/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=real+madrid&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/milan/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=milan&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/juventus/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=juventus&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/manchester/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=manchester&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/liverpool/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=liverpool&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/bayern/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=bayern&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/borussia/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=borussia&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/psg/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=psg&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/penarol/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=penarol&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/argentina/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=argentina&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/selecao/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=selecao&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/espanha/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=espanha&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/franca/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=franca&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
    "https://www.enjoei.com.br/italia/s?ref=products_search&sid=c0082dd4-87f4-46c2-b700-9f559e2e762f-1761155012593&q=italia&st%5Bsc%5D=g&st%5Bsc%5D=gg&st%5Bsc%5D=m&st%5Bsc%5D=p&pg=50&pl=300&lp=24h&u=true&sr=same_country&dep=masculino&cat=masculino-roupas",
]

STATE_FILE = Path(os.getenv("STATE_FILE", "/data/enjoei_state.json"))
HEADLESS = os.getenv("HEADLESS", "true").strip().lower() == "true"

ENVIAR_MENSAGEM_TELEGRAM = (
    os.getenv("ENVIAR_MENSAGEM_TELEGRAM", "true").strip().lower() == "true"
)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
PAGE_TIMEOUT_MS = int(os.getenv("PAGE_TIMEOUT_MS", "60000"))
WAIT_NETWORK_IDLE_MS = int(os.getenv("WAIT_NETWORK_IDLE_MS", "10000"))
SCROLL_COUNT = int(os.getenv("SCROLL_COUNT", "3"))
SCROLL_WAIT_MS = int(os.getenv("SCROLL_WAIT_MS", "1200"))

BROWSER_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-blink-features=AutomationControlled",
]


def load_previous_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            print("Aviso: arquivo de estado corrompido. Criando um novo.")
    return {"items": {}, "last_run": None}


def save_state(items):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {"last_run": datetime.now().isoformat(), "items": items}
    STATE_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def normalize_url(href: str) -> str:
    return urljoin("https://www.enjoei.com.br", href.split("?")[0].strip())


def extract_product_id(url: str) -> str:
    m = re.search(r"-([0-9]{5,})$", url.rstrip("/"))
    if m:
        return m.group(1)
    return url


def slug_to_title(url: str) -> str:
    slug = url.rstrip("/").split("/")[-1]
    slug = re.sub(r"-\d+$", "", slug)
    slug = slug.replace("-", " ")
    slug = clean_text(slug)
    return slug.title()


def escape_html(text: str) -> str:
    if text is None:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def get_search_label(search_url: str) -> str:
    parsed = urlparse(search_url)
    qs = parse_qs(parsed.query)
    q = qs.get("q", [""])[0]
    if q:
        return clean_text(unquote_plus(q)).title()

    path_parts = [p for p in parsed.path.split("/") if p]
    if path_parts:
        return clean_text(unquote_plus(path_parts[0])).title()

    return "Busca"


def build_state_key(search_label: str, product_id: str) -> str:
    return f"{search_label}::{product_id}"


def send_telegram_message(text: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID precisam estar definidos."
        )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }

    response = requests.post(url, data=payload, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Erro do Telegram: {data}")


def send_telegram_for_new_items(new_items):
    if not new_items:
        return

    if not ENVIAR_MENSAGEM_TELEGRAM:
        print("Envio para o Telegram está desativado.")
        return

    for i, item in enumerate(new_items, start=1):
        search_label = escape_html(item["search_label"])
        title = escape_html(item["title"])
        price = escape_html(item["price"] or "não identificado")
        url = escape_html(item["url"])

        text = (
            f"🆕 <b>Novo item encontrado</b>\n\n"
            f"<b>Busca:</b> {search_label}\n"
            f"<b>Título:</b> {title}\n"
            f"<b>Preço:</b> {price}\n"
            f"<b>Link:</b>\n{url}"
        )

        send_telegram_message(text)
        print(f"Mensagem enviada ao Telegram para o item {i}/{len(new_items)}.")


def scrape_single_url(page, search_url: str):
    search_label = get_search_label(search_url)

    print(f"Abrindo página: {search_label}")
    page.goto(search_url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)

    for label in ["entendi e concordo", "aceitar", "continuar", "ok"]:
        try:
            page.get_by_text(label, exact=False).click(timeout=1500)
            print(f"Banner clicado: {label}")
            break
        except Exception:
            pass

    try:
        page.wait_for_load_state("networkidle", timeout=WAIT_NETWORK_IDLE_MS)
    except PlaywrightTimeoutError:
        print("Aviso: networkidle demorou, seguindo assim mesmo.")

    print(f"Rolando a página para carregar mais itens em: {search_label}")
    for i in range(SCROLL_COUNT):
        page.mouse.wheel(0, 2500)
        page.wait_for_timeout(SCROLL_WAIT_MS)
        print(f"Rolagem {i + 1}/{SCROLL_COUNT} concluída.")

    raw = page.evaluate(
        """
    () => {
      const anchors = [...document.querySelectorAll('a[href*="/p/"]')];
      const seen = new Set();
      const kept = [];
      const skipped = [];

      function txt(el) {
        return ((el?.innerText) || "").replace(/\\s+/g, " ").trim();
      }

      function lowerTxt(el) {
        return txt(el).toLowerCase();
      }

      function getProductLinksCount(el) {
        return el.querySelectorAll('a[href*="/p/"]').length;
      }

      function looksLikeShopSection(el) {
        const t = lowerTxt(el);
        const hasShopText =
          t.includes("ver lojinha") &&
          t.includes("destaque sua loja");

        if (!hasShopText) return false;

        const productLinks = getProductLinksCount(el);
        if (productLinks < 4 || productLinks > 12) return false;

        const textLength = txt(el).length;
        if (textLength > 1500) return false;

        return true;
      }

      function collectMinimalShopSections() {
        const candidates = [...document.querySelectorAll("div, section, article")]
          .filter(looksLikeShopSection);

        const minimal = candidates.filter(el => {
          return !candidates.some(other => other !== el && el.contains(other));
        });

        return minimal;
      }

      const shopSections = collectMinimalShopSections();

      function isInsideShopSection(el) {
        return shopSections.some(section => section.contains(el));
      }

      function findBestCard(a) {
        let node = a;
        let best = a;

        for (let depth = 0; depth < 8 && node && node !== document.body; depth++) {
          node = node.parentElement;
          if (!node) break;

          const productLinks = getProductLinksCount(node);
          const text = txt(node);

          if (
            productLinks >= 1 &&
            productLinks <= 2 &&
            text.length >= 5 &&
            text.length <= 260
          ) {
            best = node;
            break;
          }
        }

        return best;
      }

      function extractPrice(card) {
        let text = txt(card);
        let matches = text.match(/R\\$\\s*\\d+[\\d\\.]*?(?:,\\d{2})?/g);
        if (matches && matches.length) {
          return matches[0].trim();
        }

        let node = card;
        for (let depth = 0; depth < 3 && node && node !== document.body; depth++) {
          node = node.parentElement;
          if (!node) break;

          const productLinks = getProductLinksCount(node);
          if (productLinks > 3) break;

          text = txt(node);
          matches = text.match(/R\\$\\s*\\d+[\\d\\.]*?(?:,\\d{2})?/g);
          if (matches && matches.length) {
            return matches[0].trim();
          }
        }

        return null;
      }

      for (const a of anchors) {
        const href = a.getAttribute("href");
        if (!href) continue;

        const key = href.split("?")[0];
        if (seen.has(key)) continue;
        seen.add(key);

        if (isInsideShopSection(a)) {
          skipped.push({
            href,
            text: txt(a),
            reason: "lojinha"
          });
          continue;
        }

        const card = findBestCard(a);

        kept.push({
          href,
          card_text: txt(card),
          price: extractPrice(card)
        });
      }

      return {
        kept,
        skipped,
        total_product_links_found: anchors.length,
        shop_sections_found: shopSections.length
      };
    }
    """
    )

    raw_items = raw["kept"]
    skipped_items = raw["skipped"]
    total_product_links_found = raw["total_product_links_found"]
    shop_sections_found = raw.get("shop_sections_found", 0)

    items = {}
    for row in raw_items:
        href = normalize_url(row["href"])
        product_id = extract_product_id(href)
        state_key = build_state_key(search_label, product_id)

        items[state_key] = {
            "state_key": state_key,
            "search_label": search_label,
            "search_url": search_url,
            "id": product_id,
            "title": slug_to_title(href),
            "price": clean_text(row.get("price") or "") or None,
            "url": href,
            "seen_at": datetime.now().isoformat(),
        }

    audit = {
        "search_label": search_label,
        "search_url": search_url,
        "total_product_links_found": total_product_links_found,
        "kept_count": len(raw_items),
        "skipped_shop_count": len(skipped_items),
        "shop_sections_found": shop_sections_found,
        "skipped_examples": skipped_items[:5],
    }

    return items, audit


def print_audit(audit):
    print("=" * 70)
    print(f"COLETA - {audit['search_label']}")
    print("=" * 70)
    print(f"URL: {audit['search_url']}")
    print(
        f"Total de links de produto encontrados no DOM: {audit['total_product_links_found']}"
    )
    print(f"Blocos de lojinha encontrados: {audit.get('shop_sections_found', 0)}")
    print(f"Itens válidos mantidos: {audit['kept_count']}")
    print(f"Itens ignorados por serem de lojinha: {audit['skipped_shop_count']}")
    print()

    examples = audit.get("skipped_examples", [])
    if examples:
        print("Exemplos de itens ignorados:")
        for i, item in enumerate(examples, start=1):
            href = normalize_url(item.get("href", ""))
            text = clean_text(item.get("text", ""))[:120]
            print(f"  [{i}] {href}")
            print(f"      Texto: {text}")
        print()


def main():
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    previous = load_previous_state()
    previous_items = previous.get("items", {})

    all_current_items = {}
    all_removed_items = []

    print(f"Arquivo de estado: {STATE_FILE}")
    print(f"Headless: {HEADLESS}")
    print(f"Envio Telegram: {ENVIAR_MENSAGEM_TELEGRAM}")
    print(f"Total de buscas configuradas: {len(URLS)}")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=BROWSER_ARGS,
        )
        page = browser.new_page(viewport={"width": 1600, "height": 2200})

        for search_url in URLS:
            try:
                current_items, audit = scrape_single_url(page, search_url)
                print_audit(audit)
                all_current_items.update(current_items)
            except Exception as e:
                print("=" * 70)
                print(f"ERRO NA BUSCA: {search_url}")
                print("=" * 70)
                print(e)
                print()

        browser.close()

    current_keys = set(all_current_items.keys())
    previous_keys = set(previous_items.keys())

    new_keys = current_keys - previous_keys
    removed_keys = previous_keys - current_keys

    all_new_items = [all_current_items[k] for k in sorted(new_keys)]
    all_removed_items = [previous_items[k] for k in sorted(removed_keys)]

    print("=" * 70)
    print("MONITOR ENJOEI - RESULTADO GERAL")
    print("=" * 70)
    print(f"Última execução salva: {previous.get('last_run')}")
    print(f"Total de buscas analisadas: {len(URLS)}")
    print(f"Itens atuais válidos encontrados: {len(all_current_items)}")
    print(f"Itens novos desde a última execução: {len(all_new_items)}")
    print(f"Itens que sumiram desde a última execução: {len(all_removed_items)}")
    print()

    if all_new_items:
        print("NOVOS ITENS:")
        for i, item in enumerate(all_new_items, start=1):
            print(f"[{i}] {item['search_label']} - {item['title']}")
            print(f"    Preço: {item['price'] or 'não identificado'}")
            print(f"    URL:   {item['url']}")
            print(f"    ID:    {item['id']}")
            print()

        try:
            send_telegram_for_new_items(all_new_items)
        except Exception as e:
            print(f"Erro ao enviar mensagem no Telegram: {e}")
            print("Os itens foram detectados, mas a mensagem não foi enviada.")
    else:
        print("Nenhum item novo encontrado.")
        print()

    if all_removed_items:
        print("ITENS QUE SUMIRAM DESDE A ÚLTIMA EXECUÇÃO:")
        for i, item in enumerate(all_removed_items[:20], start=1):
            print(f"[{i}] {item['search_label']} - {item['title']}")
            print(f"    Preço: {item.get('price') or 'não identificado'}")
            print(f"    URL:   {item['url']}")
            print()
        if len(all_removed_items) > 20:
            print(f"... e mais {len(all_removed_items) - 20} itens.")
            print()

    save_state(all_current_items)
    print(f"Estado atualizado com sucesso em: {STATE_FILE}")


if __name__ == "__main__":
    main()
