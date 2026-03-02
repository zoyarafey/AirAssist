export default function AirlineLogo({ size = 'md', className = '' }) {
  const sizes = {
    sm: { container: 'h-8', icon: 24, titleSize: 'text-sm', subtitleSize: 'text-xs' },
    md: { container: 'h-12', icon: 36, titleSize: 'text-lg', subtitleSize: 'text-xs' },
    lg: { container: 'h-20', icon: 56, titleSize: 'text-2xl', subtitleSize: 'text-sm' },
  }
  const s = sizes[size]

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div className="relative">
        <svg width={s.icon} height={s.icon} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="28" cy="28" r="28" fill="rgba(77,184,255,0.1)" />
          {/* Bird/plane wing shape */}
          <path d="M8 28 C14 20, 26 16, 38 20 L48 18 L42 26 C34 24, 22 26, 14 34 Z" fill="#4db8ff" opacity="0.9"/>
          <path d="M14 34 C20 28, 32 26, 42 30 L48 32 L44 38 C36 34, 24 34, 18 40 Z" fill="#4db8ff" opacity="0.5"/>
          <circle cx="36" cy="22" r="3" fill="white" opacity="0.8"/>
        </svg>
      </div>
      <div>
        <div className={`font-display font-bold text-white leading-none tracking-wide ${s.titleSize}`}>
          JAHAN
        </div>
        <div className={`font-body font-light tracking-[0.2em] text-sky-300 uppercase ${s.subtitleSize}`}>
          Chatbot Airlines
        </div>
      </div>
    </div>
  )
}
