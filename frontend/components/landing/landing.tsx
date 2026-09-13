"use client";
import { useState } from "react";
import {
  Headphones,
  BookOpen,
  PenLine,
  Mic,
  Lock,
  MessageSquare,
  Zap,
  Target,
  CalendarCheck,
  Timer,
  Check,
} from "lucide-react";
import { t, LANGS, type Lang } from "./i18n";

function Logo({ tone = "default" }: { tone?: "default" | "invert" }) {
  return (
    <span
      className={`inline-flex items-center gap-2 text-lg font-extrabold tracking-tight ${
        tone === "invert" ? "text-navy-foreground" : "text-navy"
      }`}
    >
      <span className="inline-flex size-8 items-center justify-center rounded-xl bg-primary text-primary-foreground">
        <MessageSquare className="size-4" aria-hidden="true" />
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
      className={`inline-flex rounded-full border p-0.5 text-xs font-semibold ${
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

export default function Landing() {
  const [lang, setLang] = useState<Lang>("uz");
  const c = t[lang];

  return (
    <div lang={lang} className="landing-page min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-50 border-b border-border/70 bg-background/85 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-5 py-3.5">
          <a href="#top" className="rounded-lg">
            <Logo />
          </a>
          <nav
            className="hidden items-center gap-7 text-sm font-medium text-muted-foreground lg:flex"
            aria-label="Main"
          >
            <a className="rounded transition-colors hover:text-foreground" href="#features">
              {c.nav.features}
            </a>
            <a className="rounded transition-colors hover:text-foreground" href="#how">
              {c.nav.how}
            </a>
            <a className="rounded transition-colors hover:text-foreground" href="#pricing">
              {c.nav.pricing}
            </a>
            <a className="rounded transition-colors hover:text-foreground" href="/login">
              {c.nav.login}
            </a>
          </nav>
          <div className="flex items-center gap-3">
            <LangSwitcher lang={lang} setLang={setLang} />
            <a
              href="/register"
              className="hidden sm:inline-block rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground shadow-sm transition-colors hover:bg-primary/90"
            >
              {c.ctaPrimary}
            </a>
          </div>
        </div>
      </header>

      <main id="top">
        {/* HERO */}
        <section className="hero-surface">
          <div className="mx-auto grid max-w-6xl items-center gap-12 px-5 py-16 md:py-24 lg:grid-cols-2">
            <div className="reveal">
              <h1 className="text-4xl leading-[1.1] font-extrabold tracking-tight text-navy sm:text-5xl">
                {c.hero.title}
              </h1>
              <p className="mt-5 max-w-xl text-lg text-muted-foreground">{c.hero.subtitle}</p>
              <div className="mt-8 flex flex-wrap items-center gap-4">
                <a
                  href="/register"
                  className="rounded-2xl bg-primary px-6 py-3.5 text-base font-semibold text-primary-foreground shadow-sm transition-transform hover:-translate-y-0.5 hover:bg-primary/90"
                >
                  {c.hero.cta}
                </a>
                <a
                  href="#how"
                  className="rounded-2xl px-3 py-3 text-base font-semibold text-navy underline-offset-4 transition-colors hover:text-primary hover:underline"
                >
                  {c.hero.secondary} →
                </a>
              </div>
              <p className="mt-3 text-sm text-muted-foreground">{c.hero.ctaNote}</p>
            </div>

            {/* Dashboard mockup placeholder */}
            <div className="reveal rounded-3xl border border-border bg-card p-5 shadow-[0_24px_60px_-40px_oklch(0.31_0.055_258/0.7)] sm:p-7">
              <p className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">
                {c.hero.mockTitle} · {lang === "uz" ? "NAMUNA" : lang === "ru" ? "ПРИМЕР" : "SAMPLE"}
              </p>
              <div className="mt-4 flex items-end justify-between rounded-2xl bg-navy px-5 py-6 text-navy-foreground">
                <div>
                  <p className="text-sm opacity-75">{c.hero.mockOverall}</p>
                  <p className="text-5xl font-extrabold">6.5</p>
                </div>
                <span className="rounded-full bg-primary px-3 py-1 text-xs font-semibold text-primary-foreground">
                  Academic
                </span>
              </div>
              <p className="mt-5 text-sm font-semibold text-navy">{c.hero.mockBand}</p>
              <ul className="mt-3 space-y-3">
                {[
                  ["Listening", 7.0, 88],
                  ["Reading", 6.5, 81],
                  ["Writing", 6.0, 75],
                ].map(([name, band, pct]) => (
                  <li key={name as string} className="text-sm">
                    <div className="flex justify-between">
                      <span className="font-medium">{name}</span>
                      <span className="text-muted-foreground">{(band as number).toFixed(1)}</span>
                    </div>
                    <div className="mt-1.5 h-2 rounded-full bg-secondary">
                      <div
                        className="h-2 rounded-full bg-primary"
                        style={{ width: `${pct as number}%` }}
                      />
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        {/* TRUST BAR */}
        <section className="border-y border-border bg-card/60">
          <ul className="mx-auto flex max-w-6xl flex-wrap items-center justify-center gap-x-10 gap-y-3 px-5 py-5 text-sm font-medium">
            {c.trust.map((item) => (
              <li key={item} className="flex items-center gap-2">
                <Check className="size-4 text-primary" aria-hidden="true" />
                {item}
              </li>
            ))}
          </ul>
        </section>

        {/* HOW IT WORKS */}
        <section id="how" className="mx-auto max-w-6xl px-5 py-20">
          <h2 className="text-center text-3xl font-bold tracking-tight text-navy sm:text-4xl">
            {c.how.title}
          </h2>
          <ol className="mt-12 grid gap-6 md:grid-cols-3">
            {c.how.steps.map((s, i) => (
              <li key={s.title} className="rounded-2xl border border-border bg-card p-6">
                <span className="inline-flex size-9 items-center justify-center rounded-xl bg-accent font-bold text-accent-foreground">
                  {i + 1}
                </span>
                <h3 className="mt-4 text-lg font-semibold text-navy">{s.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{s.text}</p>
              </li>
            ))}
          </ol>
        </section>

        {/* FEATURES */}
        <section id="features" className="border-y border-border bg-card/60">
          <div className="mx-auto max-w-6xl px-5 py-20">
            <h2 className="text-3xl font-bold tracking-tight text-navy sm:text-4xl">
              {c.features.title}
            </h2>
            <p className="mt-3 max-w-2xl text-muted-foreground">{c.features.subtitle}</p>
            <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {c.features.items.map((f, i) => {
                const Icon = skillIcons[i % skillIcons.length]!;
                return (
                  <article
                    key={f.name}
                    className="rounded-2xl border border-border bg-background p-6 transition-shadow hover:shadow-md"
                  >
                    <span className="inline-flex size-11 items-center justify-center rounded-xl bg-accent text-accent-foreground">
                      <Icon className="size-5" aria-hidden="true" />
                    </span>
                    <h3 className="mt-4 flex items-center gap-2 text-lg font-semibold text-navy">
                      {f.name}
                      {f.soon && (
                        <span className="inline-flex items-center gap-1 rounded-full bg-secondary px-2 py-0.5 text-[11px] font-semibold text-muted-foreground">
                          <Lock className="size-3" aria-hidden="true" />
                          {c.features.soon}
                        </span>
                      )}
                    </h3>
                    <p className="mt-2 text-sm text-muted-foreground">{f.text}</p>
                  </article>
                );
              })}
            </div>
          </div>
        </section>

        {/* WHY */}
        <section className="mx-auto max-w-6xl px-5 py-20">
          <h2 className="text-3xl font-bold tracking-tight text-navy sm:text-4xl">{c.why.title}</h2>
          <div className="mt-10 grid gap-6 md:grid-cols-2">
            {c.why.items.map((w, i) => {
              const Icon = whyIcons[i % whyIcons.length]!;
              return (
                <div
                  key={w.title}
                  className="flex gap-4 rounded-2xl border border-border bg-card p-6"
                >
                  <span className="inline-flex size-11 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                    <Icon className="size-5" aria-hidden="true" />
                  </span>
                  <div>
                    <h3 className="text-lg font-semibold text-navy">{w.title}</h3>
                    <p className="mt-1.5 text-sm text-muted-foreground">{w.text}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* HONEST STATUS */}
        <section id="pricing" className="mx-auto max-w-6xl px-5 pb-20">
          <div className="rounded-3xl border border-primary/25 bg-accent/50 p-8 sm:p-10">
            <span className="inline-block rounded-full bg-primary px-3 py-1 text-xs font-semibold text-primary-foreground">
              {c.status.badge}
            </span>
            <h2 className="mt-4 text-2xl font-bold text-navy sm:text-3xl">{c.status.title}</h2>
            <p className="mt-3 max-w-3xl text-base leading-relaxed text-foreground/80">
              {c.status.text}
            </p>
          </div>
        </section>

        {/* FINAL CTA */}
        <section className="bg-navy">
          <div className="mx-auto max-w-3xl px-5 py-20 text-center text-navy-foreground">
            <h2 className="text-3xl font-extrabold tracking-tight sm:text-4xl">
              {c.finalCta.title}
            </h2>
            <p className="mt-4 text-base opacity-80">{c.finalCta.text}</p>
            <a
              href="/register"
              className="mt-8 inline-block rounded-2xl bg-primary px-8 py-4 text-base font-semibold text-primary-foreground transition-transform hover:-translate-y-0.5 hover:bg-primary/90"
            >
              {c.finalCta.button}
            </a>
          </div>
        </section>
      </main>

      <footer className="bg-navy text-navy-foreground">
        <div className="mx-auto max-w-6xl border-t border-navy-foreground/15 px-5 py-10">
          <div className="flex flex-col gap-8 md:flex-row md:items-start md:justify-between">
            <div className="max-w-sm">
              <Logo tone="invert" />
              <p className="mt-3 text-sm opacity-70">{c.footer.tagline}</p>
            </div>
            <a href="/login" className="text-sm underline">{c.nav.login}</a>
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

