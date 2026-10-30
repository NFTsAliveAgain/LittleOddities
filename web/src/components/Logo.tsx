// The NFTs Alive Again mark: a sprout (things coming back to life) on a little oddity, plus wordmark.
export function Mark({ size = 40 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" aria-hidden="true">
      <path d="M32 22 C30 14 33 9 37 6" stroke="#1e1a2e" strokeWidth="5" fill="none" strokeLinecap="round" />
      <path d="M32 22 C30 14 33 9 37 6" stroke="#5dbb4a" strokeWidth="2.5" fill="none" strokeLinecap="round" />
      <path d="M36 8 C42 1 52 3 54 7 C48 12 41 12 36 8Z" fill="#8ee3b0" stroke="#1e1a2e" strokeWidth="2.5" strokeLinejoin="round" />
      <path d="M35 9 C30 3 21 4 19 8 C24 12 31 12 35 9Z" fill="#5dbb4a" stroke="#1e1a2e" strokeWidth="2.5" strokeLinejoin="round" />
      <path d="M10 42 C10 27 20 20 32 20 C44 20 54 27 54 42 C54 54 45 60 32 60 C19 60 10 54 10 42Z" fill="#c9b8f2" stroke="#1e1a2e" strokeWidth="3.5" />
      <ellipse cx="24" cy="40" rx="6.5" ry="7" fill="#fff" stroke="#1e1a2e" strokeWidth="2.5" />
      <ellipse cx="40" cy="40" rx="6.5" ry="7" fill="#fff" stroke="#1e1a2e" strokeWidth="2.5" />
      <path d="M17.5 37.5 H30.5 M33.5 37.5 H46.5" stroke="#1e1a2e" strokeWidth="2.5" strokeLinecap="round" />
      <circle cx="25" cy="42" r="2.6" fill="#1e1a2e" /><circle cx="41" cy="42" r="2.6" fill="#1e1a2e" />
      <path d="M27 51 Q33 54 38 49" stroke="#1e1a2e" strokeWidth="2.6" fill="none" strokeLinecap="round" />
    </svg>
  );
}

export default function Logo({ small = false }: { small?: boolean }) {
  return (
    <span className="inline-flex items-center gap-2">
      <Mark size={small ? 38 : 64} />
      <span className={`font-display font-black leading-none ${small ? "text-lg hidden sm:inline" : "text-3xl"}`}>
        NFTs <span className="text-butter">Alive</span> Again
      </span>
    </span>
  );
}
