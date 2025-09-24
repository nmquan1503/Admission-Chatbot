import api from "./http";

export interface ChatResponse {
    ai_response: string;
}

export const sendMessage = async (userInput: string): Promise<ChatResponse> => {
    try {
        const res = await api.post<ChatResponse>('/chat', { user_input: userInput });
        return res.data;
    }
    catch (err) {
        console.error('Failed calling chatbot: ', err);
        throw err;
    }
}