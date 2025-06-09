import { api } from './api';

export interface UserSettings {
    email: string;
    firstName: string;
    lastName: string;
    phone: string;
    language: string;
    theme: 'light' | 'dark' | 'system';
    notifications: {
        email: boolean;
        sms: boolean;
        push: boolean;
    };
}

export interface UpdateSettingsDto extends Partial<UserSettings> {
    userId: string;
}

export const settingsService = {
    getCurrentUserSettings: async () => {
        const response = await api.get<UserSettings>('/settings/current');
        return response.data;
    },

    updateSettings: async (userId: string, settings: UpdateSettingsDto) => {
        const response = await api.put<UserSettings>(`/settings/${userId}`, settings);
        return response.data;
    }
}; 