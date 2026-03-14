'use client';

import React, { useState } from 'react';

/**
 * InfoTooltip — A small ℹ icon that reveals an explanatory card on hover/tap.
 *
 * - Dark theme card with fade-in animation
 * - Accessible: button role, aria-label, keyboard focusable
 * - Mobile: toggles on tap
 * - Max width 260px
 */

interface InfoTooltipProps {
  /** Main heading shown in bold */
  title: string;
  /** Paragraph explaining what the variable does */
  description: string;
  /** Scale breakdown lines (e.g. "0–2 → Beginner") */
  scale: string[];
}

export default function InfoTooltip({ title, description, scale }: InfoTooltipProps) {
  const [visible, setVisible] = useState(false);

  return (
    <span className="relative inline-flex ml-1">
      <button
        type="button"
        className="text-gray-500 hover:text-cyan-400 transition-colors focus:outline-none
                   focus:text-cyan-400 cursor-help text-xs leading-none"
        aria-label={`Info: ${title}`}
        onMouseEnter={() => setVisible(true)}
        onMouseLeave={() => setVisible(false)}
        onFocus={() => setVisible(true)}
        onBlur={() => setVisible(false)}
        onClick={() => setVisible((v) => !v)}
      >
        ℹ
      </button>

      {visible && (
        <div
          role="tooltip"
          className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2
                     w-[260px] p-3 rounded-lg
                     bg-gray-800 border border-gray-700 shadow-xl shadow-black/40
                     animate-fade-in pointer-events-none"
        >
          {/* Arrow */}
          <div className="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0
                          border-l-[6px] border-l-transparent
                          border-r-[6px] border-r-transparent
                          border-t-[6px] border-t-gray-700" />

          <p className="text-xs font-semibold text-gray-200 mb-1">{title}</p>
          <p className="text-[11px] text-gray-400 leading-relaxed mb-2">{description}</p>

          {scale.length > 0 && (
            <div className="border-t border-gray-700 pt-1.5">
              <p className="text-[10px] text-gray-500 uppercase font-semibold mb-1">Scale</p>
              {scale.map((line, i) => (
                <p key={i} className="text-[11px] text-gray-400 leading-snug">{line}</p>
              ))}
            </div>
          )}
        </div>
      )}
    </span>
  );
}
