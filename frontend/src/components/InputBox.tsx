import { useState, useRef, useEffect } from "react"
import type { KeyboardEvent } from "react";
import { PlusIcon, PaperAirplaneIcon } from '@heroicons/react/24/solid';

interface Probs {
    onSend: (text: string) => void;
}

export default function InputBox({ onSend }: Probs) {

    const [text, setText] = useState('');
    const [error, setError] = useState(false);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const MAX_HEIGHT = 200;

    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = '0px';
            const newHeight = Math.min(textareaRef.current.scrollHeight, MAX_HEIGHT);
            textareaRef.current.style.height = newHeight + 'px';
        }
    }, [text]);

    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey && text.trim() !== '') {
            e.preventDefault();
            onSend(text.trim());
            setText('');
        }
    };

    return (
        <div className="w-full flex justify-center">
            <div className="w-full max-w-[700px] rounded-2xl bg-gray-500 flex flex-col justify-center items-center px-8 py-5">
                <textarea
                    ref={textareaRef}
                    className="w-full bg-transparent outline-none text-white resize-none"
                    placeholder="Nhập tin nhắn..."
                    value={text}
                    onChange={(e) => {
                        if (e.target.value.length <= 2000) {
                            setText(e.target.value)
                            setError(false)
                        }
                        else {
                            setError(true)
                        }
                    }}
                    onKeyDown={handleKeyDown}
                />
                {error && <div className="text-red-400 text-sm py-2">Câu hỏi quá dài</div>}
                <div className="w-full h-[40px] py-2 flex justify-between">
                    <button
                        className="cursor-pointer"
                        onClick={() => {
                            console.log('add')
                        }}
                    >
                        <PlusIcon className="w-7 h-7 text-white" />
                    </button>
                    <button
                        className={text.trim() === '' ? 'cursor-not-allowed' : 'cursor-pointer'}
                        disabled={text.trim() === ''}
                        onClick={() => {
                            if (text.trim()) {
                                onSend(text);
                                setText('')
                            }
                        }}
                    >
                        <PaperAirplaneIcon className={`w-7 h-7 ${text.trim() === '' ? 'text-gray-400' : 'text-white' }`} />
                    </button>
                </div>
            </div>
        </div>
    );
}