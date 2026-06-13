"use client";

import { useEffect, useRef, useState } from "react";
import Image from "next/image";
import Link from "next/link";

interface Slide {
  slug: string;
  badge: string;
  title: string;
  desc: string;
  ctaLabel: string;
  ctaHref: string;
}

interface Props {
  slides: Slide[];
}

export default function HeroCarousel({ slides }: Props) {
  const [active, setActive] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  function goTo(idx: number) {
    setActive(idx);
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(next, 6000);
  }

  function next() {
    setActive((prev) => (prev + 1) % slides.length);
  }

  useEffect(() => {
    timerRef.current = setInterval(next, 6000);
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [slides.length]);

  return (
    <div className="hero-carousel" role="region" aria-label="Featured schemes carousel">
      {slides.map((slide, i) => (
        <div key={slide.slug} className={`hero-slide${i === active ? " is-active" : ""}`} aria-hidden={i !== active}>
          {/* Full-bleed image */}
          <div className="hero-slide-img-wrapper">
            <Image
              src={`/scheme-images/cat-${slide.slug}.png`}
              alt=""
              fill
              priority={i === 0}
              sizes="100vw"
              className="hero-slide-img"
              aria-hidden="true"
            />
          </div>

          {/* Gradient overlay */}
          <div className="hero-slide-overlay" aria-hidden="true" />

          {/* Text overlay — centered left */}
          <div className="hero-slide-content">
            <span className="hero-slide-badge">{slide.badge}</span>
            <h1 className="hero-slide-title">{slide.title}</h1>
            <p className="hero-slide-desc">{slide.desc}</p>
            <div className="hero-actions">
              <Link href={slide.ctaHref} className="btn btn-primary btn-lg">
                {slide.ctaLabel}
                <svg width="14" height="14" fill="none" viewBox="0 0 14 14" aria-hidden="true">
                  <path d="M2 7h10M8 3l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                </svg>
              </Link>
              <Link href="/hi/check" className="btn btn-lg" style={{ color: "rgba(255,255,255,.8)", border: "1.5px solid rgba(255,255,255,.25)", background: "transparent" }}>
                पात्रता जाँचें
              </Link>
            </div>
          </div>
        </div>
      ))}

      {/* Dot indicators */}
      <div className="hero-indicators" role="tablist" aria-label="Carousel slides">
        {slides.map((slide, i) => (
          <button
            key={slide.slug}
            className={`hero-dot${i === active ? " is-active" : ""}`}
            onClick={() => goTo(i)}
            role="tab"
            aria-selected={i === active}
            aria-label={`Slide ${i + 1}: ${slide.badge}`}
          />
        ))}
      </div>

      {/* Scroll cue */}
      <div className="hero-scroll-cue" aria-hidden="true">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path d="M6 9l6 6 6-6" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>
    </div>
  );
}
