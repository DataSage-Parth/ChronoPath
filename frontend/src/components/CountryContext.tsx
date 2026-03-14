'use client';

import React from 'react';

/**
 * CountryContext — Shows regional salary, growth outlook, and opportunity index
 * based on the user's selected country.
 */

type Currency = 'USD' | 'INR';
const RATES = { USD: 1, INR: 83 } as const;

function fmt(amt: number, c: Currency): string {
  const v = amt * RATES[c];
  const sym = c === 'INR' ? '₹' : '$';
  return sym + v.toLocaleString(c === 'INR' ? 'en-IN' : 'en-US', { maximumFractionDigits: 0 });
}

interface CountryData {
  name: string;
  flag: string;
  avgSalary: number; // USD
  growthOutlook: string;
  growthColor: string;
  opportunityIndex: number; // 0-10
  notes: string;
}

const COUNTRY_DB: Record<string, CountryData> = {
  USA: {
    name: 'United States', flag: '🇺🇸', avgSalary: 95000,
    growthOutlook: 'Strong', growthColor: 'text-emerald-400',
    opportunityIndex: 9,
    notes: 'Largest tech market globally. High salaries offset by higher cost of living.',
  },
  GBR: {
    name: 'United Kingdom', flag: '🇬🇧', avgSalary: 72000,
    growthOutlook: 'Moderate', growthColor: 'text-blue-400',
    opportunityIndex: 7,
    notes: 'Strong fintech and AI sector. London is a global tech hub.',
  },
  DEU: {
    name: 'Germany', flag: '🇩🇪', avgSalary: 78000,
    growthOutlook: 'Moderate', growthColor: 'text-blue-400',
    opportunityIndex: 7,
    notes: 'Strong engineering culture. Berlin and Munich are growing tech centers.',
  },
  CAN: {
    name: 'Canada', flag: '🇨🇦', avgSalary: 70000,
    growthOutlook: 'Moderate', growthColor: 'text-blue-400',
    opportunityIndex: 7,
    notes: 'Growing AI/ML ecosystem. Toronto and Vancouver lead in tech.',
  },
  AUS: {
    name: 'Australia', flag: '🇦🇺', avgSalary: 75000,
    growthOutlook: 'Moderate', growthColor: 'text-blue-400',
    opportunityIndex: 7,
    notes: 'Strong job market with good work-life balance emphasis.',
  },
  IND: {
    name: 'India', flag: '🇮🇳', avgSalary: 18000,
    growthOutlook: 'Very Strong', growthColor: 'text-emerald-300',
    opportunityIndex: 8,
    notes: 'Fastest-growing major tech market. Rapidly rising salaries in tier-1 cities.',
  },
  BRA: {
    name: 'Brazil', flag: '🇧🇷', avgSalary: 22000,
    growthOutlook: 'Growing', growthColor: 'text-teal-400',
    opportunityIndex: 5,
    notes: 'Expanding startup ecosystem. São Paulo is the regional tech hub.',
  },
};

interface Props {
  country: string;
  currency: Currency;
}

export default function CountryContext({ country, currency }: Props) {
  const data = COUNTRY_DB[country];
  if (!data) return null;

  const oppBars = Array.from({ length: 10 }, (_, i) => i < data.opportunityIndex);

  return (
    <div className="bg-gray-900/40 backdrop-blur-sm rounded-xl border border-gray-800/60 p-5">
      <div className="flex items-center gap-2.5 mb-4">
        <div className="flex items-center justify-center w-8 h-8 rounded-lg
                        bg-gradient-to-br from-blue-500/20 to-indigo-500/20 border border-blue-500/20">
          <span className="text-base">{data.flag}</span>
        </div>
        <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">
          {data.name} Context
        </h3>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-3">
        <div className="text-center">
          <p className="text-[10px] text-gray-500 uppercase">Avg Salary</p>
          <p className="text-sm font-bold text-cyan-400">{fmt(data.avgSalary, currency)}</p>
        </div>
        <div className="text-center">
          <p className="text-[10px] text-gray-500 uppercase">Growth</p>
          <p className={`text-sm font-bold ${data.growthColor}`}>{data.growthOutlook}</p>
        </div>
        <div className="text-center">
          <p className="text-[10px] text-gray-500 uppercase">Opportunity</p>
          <div className="flex justify-center gap-0.5 mt-1">
            {oppBars.map((active, i) => (
              <div
                key={i}
                className={`w-1.5 h-3 rounded-sm ${active ? 'bg-cyan-500' : 'bg-gray-700'}`}
              />
            ))}
          </div>
        </div>
      </div>

      <p className="text-xs text-gray-500 leading-relaxed">{data.notes}</p>
    </div>
  );
}
