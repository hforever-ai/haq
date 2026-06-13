"use client";

import { useEffect, useRef } from "react";
import type { AnimationItem } from "lottie-web";

interface Props {
  src: string;           // path under /lottie/, e.g. "cat-mahila.json"
  size?: number;         // px, default 44
  loop?: boolean;        // default false — play only on hover for category tiles
  autoplay?: boolean;    // default false
  className?: string;
  style?: React.CSSProperties;
}

export default function LottiePlayer({ src, size = 44, loop = false, autoplay = false, className, style }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const animRef = useRef<AnimationItem | null>(null);

  useEffect(() => {
    let cancelled = false;
    import("lottie-web").then((mod) => {
      if (cancelled || !containerRef.current) return;
      const lottie = mod.default ?? mod;
      animRef.current = lottie.loadAnimation({
        container: containerRef.current,
        renderer: "svg",
        loop,
        autoplay,
        path: `/lottie/${src}`,
      });
    });
    return () => {
      cancelled = true;
      animRef.current?.destroy();
      animRef.current = null;
    };
  }, [src, loop, autoplay]);

  function play() { animRef.current?.play(); }
  function stop() { animRef.current?.stop(); }

  return (
    <div
      ref={containerRef}
      onMouseEnter={!autoplay ? play : undefined}
      onMouseLeave={!autoplay ? stop : undefined}
      className={className}
      style={{ width: size, height: size, flexShrink: 0, ...style }}
      aria-hidden="true"
    />
  );
}
