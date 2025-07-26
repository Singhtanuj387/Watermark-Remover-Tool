/**
 * HLS.js Configuration and Setup
 * 
 * This script configures and initializes HLS.js for adaptive streaming
 * when the browser doesn't natively support HLS.
 */

class HLSManager {
    constructor(videoElement, options = {}) {
        this.video = videoElement;
        this.options = {
            autoStartLoad: true,
            startLevel: -1, // Auto level selection
            debug: false,
            capLevelToPlayerSize: true,
            maxBufferLength: 30,
            maxMaxBufferLength: 60,
            ...options
        };
        
        this.hls = null;
        this.isSupported = Hls.isSupported();
        this.originalSrc = null;
        this.hlsUrl = null;
        
        // Initialize if video element is provided
        if (this.video) {
            this.init();
        }
    }
    
    init() {
        // Store original source
        const sourceElement = this.video.querySelector('source');
        if (sourceElement) {
            this.originalSrc = sourceElement.src;
            
            // Convert regular URL to HLS URL
            this.hlsUrl = this.getHLSUrl(this.originalSrc);
            
            // Check if HLS is supported
            if (this.isSupported) {
                this.initHLS();
            } else if (this.video.canPlayType('application/vnd.apple.mpegurl')) {
                // For Safari - native HLS support
                console.log('Using native HLS support');
                this.video.src = this.hlsUrl;
            } else {
                console.warn('HLS is not supported in this browser, falling back to original source');
                // Keep original source
            }
        } else {
            console.error('No source element found in video');
        }
    }
    
    initHLS() {
        // Destroy any existing instance
        this.destroyHLS();
        
        // Create new HLS instance
        this.hls = new Hls(this.options);
        
        // Bind events
        this.hls.on(Hls.Events.MEDIA_ATTACHED, () => {
            console.log('HLS: Media attached');
            this.hls.loadSource(this.hlsUrl);
        });
        
        this.hls.on(Hls.Events.MANIFEST_PARSED, (event, data) => {
            console.log('HLS: Manifest parsed, found ' + data.levels.length + ' quality levels');
            
            // Auto-play if specified in options
            if (this.options.autoplay) {
                this.video.play().catch(e => {
                    console.warn('Auto-play prevented:', e);
                });
            }
        });
        
        this.hls.on(Hls.Events.ERROR, (event, data) => {
            if (data.fatal) {
                switch(data.type) {
                    case Hls.ErrorTypes.NETWORK_ERROR:
                        console.error('HLS: Fatal network error', data);
                        // Try to recover
                        this.hls.startLoad();
                        break;
                    case Hls.ErrorTypes.MEDIA_ERROR:
                        console.error('HLS: Fatal media error', data);
                        // Try to recover
                        this.hls.recoverMediaError();
                        break;
                    default:
                        // Cannot recover
                        console.error('HLS: Fatal error, cannot recover', data);
                        this.destroyHLS();
                        // Fall back to original source
                        this.fallbackToOriginal();
                        break;
                }
            } else {
                console.warn('HLS: Non-fatal error', data);
            }
        });
        
        // Attach media
        this.hls.attachMedia(this.video);
    }
    
    destroyHLS() {
        if (this.hls) {
            this.hls.destroy();
            this.hls = null;
        }
    }
    
    fallbackToOriginal() {
        console.log('Falling back to original video source');
        if (this.originalSrc) {
            this.video.src = this.originalSrc;
            this.video.load();
        }
    }
    
    getHLSUrl(originalUrl) {
        // Convert regular video URL to HLS URL
        // Example: /video/file.mp4 -> /hls/file/master.m3u8
        if (!originalUrl) return null;
        
        const urlParts = originalUrl.split('?')[0]; // Remove query parameters
        const pathParts = urlParts.split('/');
        const filename = pathParts[pathParts.length - 1];
        const filenameWithoutExt = filename.split('.')[0];
        
        // Return the HLS URL with the filename (without extension)
        return `/hls/${filenameWithoutExt}/master.m3u8`;
    }
    
    // Public methods for quality control
    setQualityLevel(level) {
        if (this.hls) {
            this.hls.currentLevel = level;
        }
    }
    
    getQualityLevels() {
        if (this.hls && this.hls.levels) {
            return this.hls.levels.map((level, index) => {
                return {
                    index: index,
                    height: level.height,
                    width: level.width,
                    bitrate: level.bitrate,
                    name: `${level.height}p (${Math.round(level.bitrate / 1000)} kbps)`
                };
            });
        }
        return [];
    }
    
    getCurrentQualityLevel() {
        if (this.hls) {
            return this.hls.currentLevel;
        }
        return -1;
    }
}

// Export for use in other scripts
window.HLSManager = HLSManager;