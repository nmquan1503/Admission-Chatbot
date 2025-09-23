import { useState, useRef, useEffect } from "react";
import type { Message } from '../types'
import MessageList from "./MessageList";
import InputBox from "./InputBox";

export default function ChatWindow() {

    const [messages, setMessages] = useState<Message[]>([]);
    const containerRef = useRef<HTMLDivElement | null>(null);

    const sendMessage = (text: string) => {
        const newMessage: Message = { text, sender: 'user' };
        setMessages((prev) => [...prev, newMessage]);
        setTimeout(() => {
            setMessages((prev) => [...prev, {text: 'bot', sender: 'ai'}]);
        }, 500);
    }

    useEffect(() => {
        if (containerRef.current) {
            containerRef.current.scrollTop = containerRef.current.scrollHeight;
        }
    }, [messages])

    return (
        <div className={`w-full h-full flex flex-col gap-[3px] pb-[30px] pt-[20px] ${messages.length === 0 ? 'justify-center items-center' : 'justify-between'}` }>
            <div ref={containerRef} className="w-full overflow-auto px-[20px] scroll-smooth">
                {messages.length === 0 ? (
                    <div className="flex-1 flex flex-col items-center justify-center text-center px-6">
                        <h1 className="text-3xl font-bold mb-4 text-gray-800">
                            Chatbot tuyển sinh 🎓
                        </h1>
                        <h2 className="text-2xl font-semibold text-gray-700 mb-3">
                            Trường Đại học Công nghệ – ĐHQGHN
                        </h2>
                        <p className="text-base text-gray-500 max-w-lg">
                            Xin chào! Tôi là trợ lý ảo có thể hỗ trợ bạn về <br />
                            thông tin tuyển sinh, ngành học, học phí và các thắc mắc liên quan.  
                            Hãy bắt đầu bằng cách nhập tin nhắn bên dưới 👇
                        </p>
                    </div>
                ) : (
                    <MessageList messages={messages} />
                )}
            </div>
            <div className="w-full px-[20px]">
                <InputBox onSend={sendMessage} />
            </div>
        </div>
    )

}