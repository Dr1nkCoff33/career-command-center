'use client';

import React from 'react';
import { Building2, MapPin } from 'lucide-react';
import { Company } from '@/types';
import styles from './CompanySelector.module.css';

interface CompanySelectorProps {
  companies: Record<string, Company>;
  selectedCompany: string;
  selectedLocations: string[];
  onCompanyChange: (company: string) => void;
  onLocationToggle: (location: string) => void;
}

export const CompanySelector: React.FC<CompanySelectorProps> = ({
  companies,
  selectedCompany,
  selectedLocations,
  onCompanyChange,
  onLocationToggle,
}) => {
  const currentCompany = companies[selectedCompany];

  return (
    <div className={styles.container}>
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Select Company
        </label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {Object.entries(companies).map(([key, company]) => (
            <button
              key={key}
              onClick={() => onCompanyChange(key)}
              className={`${styles.companyCard} ${
                selectedCompany === key ? styles.selected : ''
              } p-4 border-2 rounded-lg transition-all hover:shadow-md`}
            >
              <Building2 className="w-5 h-5 mb-2" />
              <span className="font-medium">{company.name}</span>
            </button>
          ))}
        </div>
      </div>

      {currentCompany && (
        <div className="animate-fade-in">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Select Locations
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {currentCompany.locations.map((location) => (
              <label
                key={location}
                className={`${styles.locationCard} ${
                  selectedLocations.includes(location) ? styles.selected : ''
                } flex items-center p-3 border-2 rounded-lg cursor-pointer transition-all hover:shadow-sm`}
              >
                <input
                  type="checkbox"
                  checked={selectedLocations.includes(location)}
                  onChange={() => onLocationToggle(location)}
                  className="sr-only"
                />
                <MapPin className="w-4 h-4 mr-2" />
                <span>{location}</span>
              </label>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};