// Types
export interface ProcessedImage {
    text: string;
    confidence: number;
    processingTime: number;
}

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5006';

// Function to check if backend is available
export const checkBackendStatus = async (): Promise<boolean> => {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        return response.ok;
    } catch (error) {
        console.error('Backend health check failed:', error);
        return false;
    }
};

// Function to get available backend port
export const getBackendPort = async (): Promise<number> => {
    const ports = [5006, 5007, 5008, 5009];
    for (const port of ports) {
        try {
            const response = await fetch(`http://localhost:${port}/health`);
            if (response.ok) {
                return port;
            }
        } catch (error) {
            continue;
        }
    }
    throw new Error('No available backend port found');
};

// Update API calls to use dynamic port
export const processImage = async (imageData: string): Promise<ProcessedImage> => {
    try {
        const port = await getBackendPort();
        const response = await fetch(`http://localhost:${port}/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image: imageData }),
        });
        
        if (!response.ok) {
            throw new Error('Failed to process image');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error processing image:', error);
        throw error;
    }
}; 