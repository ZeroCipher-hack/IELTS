"use client";
import { useState } from "react";
import {
  Headphones,
  BookOpen,
  PenLine,
  Mic,
  Lock,
  Zap,
  Target,
  CalendarCheck,
  Timer,
  Check,
  ArrowUpRight,
  Pencil,
  Sparkles,
} from "lucide-react";
import { t, LANGS, type Lang } from "./i18n";

function Logo({ tone = "default" }: { tone?: "default" | "invert" }) {
  return (
    <span
      className={`inline-flex items-center gap-2 text-lg font-extrabold tracking-tight ${
        tone === "invert" ? "text-navy-foreground" : "text-navy"
      }`}
    >
      <span className="inline-flex size-8 items-center justify-center rounded-xl bg-primary text-primary-foreground rotate-3">
        <Sparkles className="size-4" aria-hidden="true" />
      </span>
      IELTSQA
    </span>
  );
}

function LangSwitcher({
  lang,
  setLang,
  tone = "default",
}: {
  lang: Lang;
  setLang: (l: Lang) => void;
  tone?: "default" | "invert";
}) {
  return (
    <div
      className={`inline-flex rounded-full border p-0.5 text-xs font-bold ${
        tone === "invert" ? "border-navy-foreground/25" : "border-border bg-card"
      }`}
      role="group"
      aria-label="Language"
    >
      {LANGS.map((l) => (
        <button
          key={l}
          type="button"
          onClick={() => setLang(l)}
          aria-pressed={lang === l}
          className={`rounded-full px-2.5 py-1 uppercase transition-colors ${
            lang === l
              ? "bg-primary text-primary-foreground"
              : tone === "invert"
                ? "text-navy-foreground/70 hover:text-navy-foreground"
                : "text-muted-foreground hover:text-foreground"
          }`}
        >
          {l}
        </button>
      ))}
    </div>
  );
}

const skillIcons = [Headphones, BookOpen, PenLine, Mic];
const whyIcons = [Zap, Target, CalendarCheck, Timer];
const cardColors = [
  { bg: "bg-[var(--signal-1)]", fg: "text-white", chip: "bg-white/15" },
  { bg: "bg-[var(--signal-2)]", fg: "text-white", chip: "bg-white/15" },
  { bg: "bg-[var(--signal-3)]", fg: "text-[var(--navy)]", chip: "bg-black/10" },
  { bg: "bg-[var(--signal-4)]", fg: "text-white", chip: "bg-white/15" },
];

export default function Landing() {
  const [lang, setLang] = useState<Lang>("uz");
  const c = t[lang];

  return (
    <div lang={lang} className="landing-page min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-50 px-4 pt-4 sm:px-6">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 rounded-full bg-white/90 px-5 py-2.5 shadow-[0_10px_30px_-12px_rgba(26,26,46,0.35)] backdrop-blur">
          <a href="#top" className="rounded-lg">
            <Logo />
          </a>
          <nav
            className="hidden items-center gap-7 text-sm font-semibold text-navy/70 lg:flex"
            aria-label="Main"
          >
            <a className="rounded transition-colors hover:text-navy" href="#features">
              {c.nav.features}
            </a>
            <a className="rounded transition-colors hover:text-navy" href="#how">
              {c.nav.how}
            </a>
            <a className="rounded transition-colors hover:text-navy" href="#pricing">
              {c.nav.pricing}
            </a>
            <a className="rounded transition-colors hover:text-navy" href="/login">
              {c.nav.login}
            </a>
          </nav>
          <div className="flex items-center gap-3">
            <LangSwitcher lang={lang} setLang={setLang} />
            <a
              href="/register"
              className="hidden rounded-full bg-primary px-4 py-2 text-sm font-bold text-primary-foreground shadow-sm transition-colors hover:bg-[var(--primary-hover)] sm:inline-block"
            >
              {c.ctaPrimary}
            </a>
          </div>
        </div>
      </header>

      <main id="top">
        <section className="hero-surface relative overflow-hidden">
          <div className="mx-auto max-w-6xl px-4 pt-10 pb-16 sm:px-6 md:pt-14">
            <div className="relative grid gap-10 overflow-hidden rounded-[2.5rem] bg-primary px-6 py-12 sm:px-10 md:py-16 lg:grid-cols-2 lg:items-center">
              <div
                aria-hidden="true"
                className="pointer-events-none absolute -right-24 top-1/2 size-[420px] -translate-y-1/2 rounded-full border-[3px] border-dashed border-white/25"
              />
              <div
                aria-hidden="true"
                className="pointer-events-none absolute right-16 top-10 size-3 rounded-full bg-[var(--signal-3)]"
              />

              <div className="relative">
                <span className="inline-flex items-center gap-1.5 rounded-full bg-[var(--signal-3)] px-3 py-1 text-xs font-extrabold text-navy">
                  IELTS Academic
                </span>
                <h1 className="mt-5 text-4xl leading-[1.08] font-extrabold tracking-tight text-white sm:text-5xl">
                  {c.hero.title}
                </h1>
                <p className="mt-5 max-w-xl text-base text-white/80 sm:text-lg">
                  {c.hero.subtitle}
                </p>
                <div className="mt-8 flex flex-wrap items-center gap-4">
                  <a
                    href="/register"
                    className="inline-flex items-center gap-2 rounded-full bg-[var(--signal-3)] px-6 py-3.5 text-base font-extrabold text-navy shadow-[0_10px_0_0_rgba(0,0,0,0.15)] transition-transform hover:-translate-y-0.5 active:translate-y-0 active:shadow-none"
                  >
                    {c.hero.cta}
                  </a>
                  <a
                    href="#how"
                    className="inline-flex items-center gap-1.5 rounded-full px-3 py-3 text-base font-bold text-white underline-offset-4 transition-colors hover:underline"
                  >
                    {c.hero.secondary} <ArrowUpRight className="size-4" aria-hidden="true" />
                  </a>
                </div>
                <p className="mt-3 text-sm text-white/60">{c.hero.ctaNote}</p>
              </div>

              <div className="relative">
                <div className="relative mx-auto max-w-sm rounded-3xl bg-white p-6 shadow-[0_30px_60px_-20px_rgba(0,0,0,0.45)]">
                  <p className="text-xs font-extrabold tracking-wide text-muted-foreground uppercase">
                    {c.hero.mockTitle}
                  </p>
                  <div className="mt-4 flex items-end justify-between rounded-2xl bg-navy px-5 py-6 text-navy-foreground">
                    <div>
                      <p className="text-sm opacity-75">{c.hero.mockOverall}</p>
                      <p className="text-5xl font-extrabold">6.5</p>
                    </div>
                    <span className="rounded-full bg-[var(--signal-3)] px-3 py-1 text-xs font-extrabold text-navy">
                      Academic
                    </span>
                  </div>
                  <p className="mt-5 text-sm font-bold text-navy">{c.hero.mockBand}</p>
                  <ul className="mt-3 space-y-3">
                    {[
                      ["Listening", 7.0, 88, "var(--signal-2)"],
                      ["Reading", 6.5, 81, "var(--primary)"],
                      ["Writing", 6.0, 75, "var(--signal-4)"],
                    ].map(([name, band, pct, color]) => (
                      <li key={name as string} className="text-sm">
                        <div className="flex justify-between">
                          <span className="font-semibold text-navy">{name}</span>
                          <span className="text-muted-foreground">{(band as number).toFixed(1)}</span>
                        </div>
                        <div className="mt-1.5 h-2 rounded-full bg-secondary">
                          <div
                            className="h-2 rounded-full"
                            style={{ width: `${pct as number}%`, background: color as string }}
                          />
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="paper-tilt absolute -left-6 -bottom-6 hidden rounded-2xl bg-white px-4 py-3 shadow-lg sm:flex sm:items-center sm:gap-2">
                  <Pencil className="size-5 text-[var(--signal-4)]" aria-hidden="true" />
                  <span className="text-xs font-bold text-navy">Bepul urinish</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="bg-background">
          <ul className="mx-auto flex max-w-6xl flex-wrap items-center justify-center gap-x-10 gap-y-3 px-5 pb-10 text-sm font-bold text-navy">
            {c.trust.map((item) => (
              <li key={item} className="flex items-center gap-2">
                <span className="inline-flex size-5 items-center justify-center rounded-full bg-navy text-white">
                  <Check className="size-3" aria-hidden="true" />
                </span>
                {item}
              </li>
            ))}
          </ul>
        </section>

        <section id="features" className="bg-white">
          <div className="mx-auto max-w-6xl px-5 py-20">
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div>
                <h2 className="text-3xl font-extrabold tracking-tight text-navy sm:text-4xl">
                  {c.features.title}
                </h2>
                <p className="mt-3 max-w-2xl text-muted-foreground">{c.features.subtitle}</p>
              </div>
            </div>
            <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
              {c.features.items.map((f, i) => {
                const Icon = skillIcons[i % skillIcons.length]!;
                const palette = cardColors[i % cardColors.length]!;
                return (
                  <article
                    key={f.name}
                    className={`relative flex flex-col justify-between rounded-3xl p-6 transition-transform hover:-translate-y-1 ${palette.bg} ${palette.fg}`}
                  >
                    <div>
                      <span
                        className={`inline-flex size-11 items-center justify-center rounded-xl ${palette.chip}`}
                      >
                        <Icon className="size-5" aria-hidden="true" />
                      </span>
                      <h3 className="mt-4 flex flex-wrap items-center gap-2 text-lg font-extrabold">
                        {f.name}
                        {f.soon && (
                          <span className="inline-flex items-center gap-1 rounded-full bg-black/15 px-2 py-0.5 text-[11px] font-bold">
                            <Lock className="size-3" aria-hidden="true" />
                            {c.features.soon}
                          </span>
                        )}
                      </h3>
                      <p className="mt-2 text-sm opacity-85">{f.text}</p>
                    </div>
                  </article>
                );
              })}
            </div>
          </div>
        </section>

        <section id="how" className="bg-background">
          <div className="mx-auto max-w-6xl px-5 py-20">
            <h2 className="text-3xl font-extrabold tracking-tight text-navy sm:text-4xl">
              {c.how.title}
            </h2>
            <ol className="mt-12 grid gap-6 md:grid-cols-3">
              {c.how.steps.map((s, i) => (
                <li key={s.title} className="rounded-3xl bg-white p-6 shadow-[0_16px_40px_-24px_rgba(26,26,46,0.35)]">
                  <span className="inline-flex size-10 items-center justify-center rounded-full bg-navy text-base font-extrabold text-white">
                    {i + 1}
                  </span>
                  <h3 className="mt-4 text-lg font-bold text-navy">{s.title}</h3>
                  <p className="mt-2 text-sm text-muted-foreground">{s.text}</p>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section className="bg-white">
          <div className="mx-auto max-w-6xl px-5 py-20">
            <h2 className="text-3xl font-extrabold tracking-tight text-navy sm:text-4xl">
              {c.why.title}
            </h2>
            <div className="mt-10 grid gap-5 md:grid-cols-2">
              {c.why.items.map((w, i) => {
                const Icon = whyIcons[i % whyIcons.length]!;
                return (
                  <div
                    key={w.title}
                    className="flex gap-4 rounded-3xl bg-background/60 p-6 ring-1 ring-border/60"
                  >
                    <span className="inline-flex size-11 shrink-0 items-center justify-center rounded-2xl bg-primary/10 text-primary">
                      <Icon className="size-5" aria-hidden="true" />
                    </span>
                    <div>
                      <h3 className="text-lg font-bold text-navy">{w.title}</h3>
                      <p className="mt-1.5 text-sm text-muted-foreground">{w.text}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        <section id="pricing" className="mx-auto max-w-6xl px-5 pb-20">
          <div className="rounded-[2rem] bg-navy p-8 text-white sm:p-10">
            <span className="inline-block rounded-full bg-[var(--signal-3)] px-3 py-1 text-xs font-extrabold text-navy">
              {c.status.badge}
            </span>
            <h2 className="mt-4 text-2xl font-extrabold sm:text-3xl">{c.status.title}</h2>
            <p className="mt-3 max-w-3xl text-base leading-relaxed text-white/75">
              {c.status.text}
            </p>
          </div>
        </section>

        <section className="bg-background">
          <div className="mx-auto max-w-3xl px-5 py-20 text-center">
            <h2 className="text-3xl font-extrabold tracking-tight text-navy sm:text-4xl">
              {c.finalCta.title}
            </h2>
            <p className="mt-4 text-base text-navy/70">{c.finalCta.text}</p>
            <a
              href="/register"
              className="mt-8 inline-block rounded-full bg-primary px-8 py-4 text-base font-extrabold text-primary-foreground shadow-[0_10px_0_0_rgba(0,0,0,0.15)] transition-transform hover:-translate-y-0.5 active:translate-y-0 active:shadow-none"
            >
              {c.finalCta.button}
            </a>
          </div>
        </section>
      </main>

      <footer className="bg-navy text-navy-foreground">
        <div className="mx-auto max-w-6xl px-5 py-10">
          <div className="flex flex-col gap-8 border-t border-white/10 pt-8 md:flex-row md:items-start md:justify-between">
            <div className="max-w-sm">
              <Logo tone="invert" />
              <p className="mt-3 text-sm opacity-70">{c.footer.tagline}</p>
            </div>
            <a href="/login" className="text-sm font-semibold underline">{c.nav.login}</a>
            <LangSwitcher lang={lang} setLang={setLang} tone="invert" />
          </div>
          <p className="mt-8 text-xs opacity-60">
            © {new Date().getFullYear()} IELTSQA. {c.footer.rights}
          </p>
        </div>
      </footer>
    </div>
  );
}
