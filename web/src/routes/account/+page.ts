import type { Load } from '@sveltejs/kit';
import { apiFetch } from '$lib/api';

interface User {
    username: string;
    email: string;
    pref_theme: 'light' | 'dark';
    full_name: string;
    default_prompt: string;
}

export const load: Load<{ user: User | null }> = async () => {
    try {
        const user = await apiFetch('/api/user/', {
            method: 'GET'
          });
        return { user };
    } catch (error) {
        console.error(error);
        return { user: null };
    }
};