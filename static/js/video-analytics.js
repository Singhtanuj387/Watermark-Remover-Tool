/**
 * Video Analytics and Performance Monitoring
 * 
 * This script tracks video playback performance metrics and reports them
 * for analysis and debugging purposes.
 */

class VideoAnalytics {
    constructor(videoElement, options = {}) {
        this.video = videoElement;
        this.options = {
            sampleInterval: options.sampleInterval || 5000, // ms
            reportEndpoint: options.reportEndpoint || null,
            debugMode: options.debugMode || false,
            ...options
        };
        
        this.metrics = {
            loadTime: null,
            bufferingEvents: 0,
            bufferingDuration: 0,
            playbackErrors: [],
            qualityChanges: 0,
            playbackRate: 1,
            resolution: null,
            networkInfo: {}
        };
        
        this.startTime = performance.now();
        this.isBuffering = false;
        this.bufferingStartTime = null;
        this.sampleInterval = null;
        
        this.init();
    }
    
    init() {
        // Attach event listeners
        this.attachEventListeners();
        
        // Start periodic sampling
        this.startSampling();
        
        // Log initialization
        this.log('Video analytics initialized');
    }
    
    attachEventListeners() {
        // Playback events
        this.video.addEventListener('loadeddata', this.onLoaded.bind(this));
        this.video.addEventListener('playing', this.onPlaying.bind(this));
        this.video.addEventListener('pause', this.onPause.bind(this));
        this.video.addEventListener('seeking', this.onSeeking.bind(this));
        this.video.addEventListener('seeked', this.onSeeked.bind(this));
        this.video.addEventListener('waiting', this.onBufferingStart.bind(this));
        this.video.addEventListener('canplay', this.onBufferingEnd.bind(this));
        this.video.addEventListener('error', this.onError.bind(this));
        this.video.addEventListener('ratechange', this.onRateChange.bind(this));
        
        // Add unload event to send final report
        window.addEventListener('beforeunload', this.sendReport.bind(this));
    }
    
    startSampling() {
        this.sampleInterval = setInterval(() => {
            this.sampleMetrics();
        }, this.options.sampleInterval);
    }
    
    stopSampling() {
        if (this.sampleInterval) {
            clearInterval(this.sampleInterval);
            this.sampleInterval = null;
        }
    }
    
    // Event handlers
    onLoaded() {
        this.metrics.loadTime = performance.now() - this.startTime;
        this.metrics.resolution = {
            width: this.video.videoWidth,
            height: this.video.videoHeight
        };
        this.log(`Video loaded in ${this.metrics.loadTime.toFixed(2)}ms`);
    }
    
    onPlaying() {
        this.log('Video playback started');
    }
    
    onPause() {
        this.log('Video paused');
    }
    
    onSeeking() {
        this.log('User seeking');
    }
    
    onSeeked() {
        this.log('Seek completed');
    }
    
    onBufferingStart() {
        if (!this.isBuffering) {
            this.isBuffering = true;
            this.bufferingStartTime = performance.now();
            this.metrics.bufferingEvents++;
            this.log('Buffering started');
        }
    }
    
    onBufferingEnd() {
        if (this.isBuffering) {
            const duration = performance.now() - this.bufferingStartTime;
            this.metrics.bufferingDuration += duration;
            this.isBuffering = false;
            this.log(`Buffering ended after ${duration.toFixed(2)}ms`);
        }
    }
    
    onError(event) {
        const error = this.video.error;
        const errorInfo = {
            code: error ? error.code : 'unknown',
            message: error ? error.message : 'unknown error',
            timestamp: new Date().toISOString()
        };
        
        this.metrics.playbackErrors.push(errorInfo);
        this.log('Video error: ' + JSON.stringify(errorInfo), 'error');
        
        // Send report immediately on error
        this.sendReport();
    }
    
    onRateChange() {
        this.metrics.playbackRate = this.video.playbackRate;
        this.log(`Playback rate changed to ${this.metrics.playbackRate}x`);
    }
    
    // Sampling and reporting
    sampleMetrics() {
        // Sample network information if available
        if (navigator.connection) {
            this.metrics.networkInfo = {
                downlink: navigator.connection.downlink,
                effectiveType: navigator.connection.effectiveType,
                rtt: navigator.connection.rtt,
                saveData: navigator.connection.saveData
            };
        }
        
        // Sample buffer health
        const buffered = this.video.buffered;
        let bufferHealth = 0;
        
        if (buffered.length > 0) {
            bufferHealth = buffered.end(buffered.length - 1) - this.video.currentTime;
        }
        
        this.metrics.bufferHealth = bufferHealth;
        
        this.log(`Buffer health: ${bufferHealth.toFixed(2)}s`);
        
        // Optional: send periodic reports
        if (this.options.sendPeriodicReports) {
            this.sendReport();
        }
    }
    
    sendReport() {
        // Add final metrics
        this.metrics.totalPlayTime = performance.now() - this.startTime;
        this.metrics.reportTime = new Date().toISOString();
        
        // Log the report
        this.log('Performance report: ' + JSON.stringify(this.metrics));
        
        // Send to endpoint if configured
        if (this.options.reportEndpoint) {
            try {
                fetch(this.options.reportEndpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.metrics)
                }).catch(err => {
                    console.error('Failed to send analytics report:', err);
                });
            } catch (e) {
                console.error('Error sending analytics report:', e);
            }
        }
    }
    
    log(message, level = 'info') {
        if (this.options.debugMode) {
            if (level === 'error') {
                console.error(`[VideoAnalytics] ${message}`);
            } else {
                console.log(`[VideoAnalytics] ${message}`);
            }
        }
    }
}

// Export for use in other scripts
window.VideoAnalytics = VideoAnalytics;