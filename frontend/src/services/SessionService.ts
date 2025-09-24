import api from "./http";

export const initSession = async () => {
    try {
        await api.get('/sessions');
        return true;
    }
    catch (err) {
        console.error('Failed init session:', err);
        return false;
    }
}