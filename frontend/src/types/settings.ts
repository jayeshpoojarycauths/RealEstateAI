export type Language = 'en' | 'es' | 'fr';
export type Theme = 'light' | 'dark' | 'system';

export interface Profile {
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
  avatar?: string;
}

export interface Preferences {
  language: Language;
  theme: Theme;
  timezone: string;
  dateFormat: string;
  currency: string;
}

export interface Notifications {
  email: {
    marketing: boolean;
    updates: boolean;
    security: boolean;
  };
  push: {
    marketing: boolean;
    updates: boolean;
    security: boolean;
  };
  sms: {
    marketing: boolean;
    updates: boolean;
    security: boolean;
  };
}

export interface UserSettings {
  id: string;
  userId: string;
  profile: Profile;
  preferences: Preferences;
  notifications: Notifications;
  createdAt: string;
  updatedAt: string;
}

export interface UpdateSettingsDto {
  profile?: Partial<Profile>;
  preferences?: Partial<Preferences>;
  notifications?: Partial<Notifications>;
} 