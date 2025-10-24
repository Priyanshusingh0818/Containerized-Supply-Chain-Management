import React, { createContext, useContext, useEffect } from 'react';
import { io } from 'socket.io-client';
import { toast } from 'react-hot-toast';
import config from '../config';

// Get the WebSocket URL from the API URL
const getWebSocketUrl = () => {
    const apiUrl = config.API_URL;
    return apiUrl.replace('http://', 'ws://').replace('https://', 'wss://').replace('/api', '');
};

const SocketContext = createContext(null);

export const useSocket = () => useContext(SocketContext);

export const SocketProvider = ({ children }) => {
    const socket = io(getWebSocketUrl(), {
        transports: ['websocket'],
        autoConnect: true
    });

    useEffect(() => {
        socket.on('connect', () => {
            console.log('Connected to WebSocket');
        });

        socket.on('inventory_update', (data) => {
            const { type, action, resource_id, audit } = data;
            
            // Show toast notification
            const message = `${action} ${type.split('_')[0]} #${resource_id}`;
            toast(message, {
                icon: action === 'CREATE' ? '➕' : action === 'UPDATE' ? '📝' : '❌'
            });
        });

        return () => {
            socket.disconnect();
        };
    }, [socket]);

    return (
        <SocketContext.Provider value={socket}>
            {children}
        </SocketContext.Provider>
    );
};