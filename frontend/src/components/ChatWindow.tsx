import { useState, useRef, useEffect } from "react";
import type { Message } from '../types'
import MessageList from "./MessageList";
import InputBox from "./InputBox";

export default function ChatWindow() {

    const [messages, setMessages] = useState<Message[]>([]);

    const messageEndRef = useRef<HTMLDivElement | null>(null);

    const scrollToBottom = () => {
        messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages])

    const sendMessage = (text: string) => {
        // const newMessage: Message = { text, sender: 'user' };
        // setMessages((prev) => [...prev, newMessage]);
        // setTimeout(() => {
        //     setMessages((prev) => [...prev, {text: 'bot', sender: 'ai'}]);
        // }, 500);
    }

    return (
        <div className="relative w-full h-full">
            <div className="relative w-full h-[calc(100%-55px)] overflow-hidden">
                <MessageList messages={messages} />
                <div ref={messageEndRef} />
            </div>
            <div className="absolute bottom-[30px] w-full">
                <InputBox onSend={sendMessage} />
            </div>
        </div>
    )

}