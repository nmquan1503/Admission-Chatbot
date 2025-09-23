import ChatWindow from "../components/ChatWindow"
import background from '../assets/background.jpg';

export default function ChatPage() {
    return (
        <div className="relative w-full h-screen overflow-hidden">
            <img 
                src={background}
                className="absolute z-0 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 min-w-full min-h-full"
                alt=""
            />
            <div className="relative z-1 w-full h-full">
                <ChatWindow />
            </div>
        </div>
    )
}