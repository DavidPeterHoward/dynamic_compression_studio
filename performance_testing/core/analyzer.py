"""
Web Performance Analyzer - Advanced analysis and optimization recommendations
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import aiohttp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from metrics.metrics import PerformanceMetrics, LoadingTimeMetrics
from utils.config import TestConfig

logger = logging.getLogger(__name__)

@dataclass
class OptimizationRecommendation:
    """Individual optimization recommendation"""
    category: str
    priority: str  # 'high', 'medium', 'low'
    title: str
    description: str
    impact: str
    effort: str
    implementation: str
    expected_improvement: str

@dataclass
class BundleAnalysis:
    """JavaScript bundle analysis"""
    total_size: int
    gzipped_size: int
    largest_chunks: List[Dict[str, Any]]
    unused_code_percentage: float
    duplicate_modules: List[str]
    optimization_opportunities: List[str]

class WebPerformanceAnalyzer:
    """
    Advanced web performance analysis and optimization recommendations
    """
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.analysis_results: Dict[str, Any] = {}
        
    async def analyze_application(self, base_url: str, tabs: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Comprehensive application performance analysis
        
        Args:
            base_url: Base URL of the application
            tabs: List of tab configurations
            
        Returns:
            Comprehensive analysis results
        """
        logger.info("Starting comprehensive performance analysis")
        
        analysis = {
            'bundle_analysis': await self._analyze_bundles(base_url),
            'resource_analysis': await self._analyze_resources(base_url, tabs),
            'rendering_analysis': await self._analyze_rendering(base_url, tabs),
            'network_analysis': await self._analyze_network(base_url, tabs),
            'memory_analysis': await self._analyze_memory(base_url, tabs),
            'accessibility_analysis': await self._analyze_accessibility(base_url, tabs),
            'seo_analysis': await self._analyze_seo(base_url, tabs),
            'recommendations': []
        }
        
        # Generate comprehensive recommendations
        analysis['recommendations'] = self._generate_comprehensive_recommendations(analysis)
        
        self.analysis_results = analysis
        return analysis
    
    async def _analyze_bundles(self, base_url: str) -> BundleAnalysis:
        """Analyze JavaScript bundles and dependencies"""
        logger.info("Analyzing JavaScript bundles")
        
        driver = self._setup_browser()
        
        try:
            driver.get(base_url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get bundle information
            bundle_info = driver.execute_script("""
                const scripts = Array.from(document.querySelectorAll('script[src]'));
                const totalSize = scripts.reduce((acc, script) => {
                    // This is a simplified calculation
                    // In real implementation, you'd fetch and measure actual sizes
                    return acc + (script.src.length * 100); // Rough estimate
                }, 0);
                
                return {
                    totalScripts: scripts.length,
                    totalSize: totalSize,
                    scriptSources: scripts.map(s => s.src)
                };
            """)
            
            return BundleAnalysis(
                total_size=bundle_info.get('totalSize', 0),
                gzipped_size=int(bundle_info.get('totalSize', 0) * 0.3),  # Estimate
                largest_chunks=[],
                unused_code_percentage=25.0,  # Estimate
                duplicate_modules=[],
                optimization_opportunities=[
                    "Consider code splitting for large bundles",
                    "Remove unused dependencies",
                    "Implement tree shaking",
                    "Use dynamic imports for route-based code splitting"
                ]
            )
            
        finally:
            driver.quit()
    
    async def _analyze_resources(self, base_url: str, tabs: List[Dict[str, str]]) -> Dict[str, Any]:
        """Analyze resource loading and optimization"""
        logger.info("Analyzing resource loading")
        
        resource_analysis = {
            'images': {'total': 0, 'optimized': 0, 'unoptimized': 0, 'recommendations': []},
            'css': {'total_size': 0, 'unused_css': 0, 'recommendations': []},
            'javascript': {'total_size': 0, 'unused_js': 0, 'recommendations': []},
            'fonts': {'total': 0, 'web_fonts': 0, 'recommendations': []}
        }
        
        driver = self._setup_browser()
        
        try:
            for tab in tabs:
                url = f"{base_url}{tab['path']}"
                driver.get(url)
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Analyze images
                images = driver.execute_script("""
                    const images = Array.from(document.querySelectorAll('img'));
                    return images.map(img => ({
                        src: img.src,
                        width: img.naturalWidth,
                        height: img.naturalHeight,
                        alt: img.alt,
                        loading: img.loading
                    }));
                """)
                
                resource_analysis['images']['total'] += len(images)
                
                # Check for unoptimized images
                for img in images:
                    if not img.get('alt'):
                        resource_analysis['images']['unoptimized'] += 1
                    if img.get('loading') != 'lazy':
                        resource_analysis['images']['unoptimized'] += 1
                
                # Analyze CSS
                css_info = driver.execute_script("""
                    const links = Array.from(document.querySelectorAll('link[rel="stylesheet"]'));
                    return {
                        total: links.length,
                        sizes: links.map(link => link.href.length * 50) // Rough estimate
                    };
                """)
                
                resource_analysis['css']['total_size'] += sum(css_info.get('sizes', []))
                
                # Analyze JavaScript
                js_info = driver.execute_script("""
                    const scripts = Array.from(document.querySelectorAll('script[src]'));
                    return {
                        total: scripts.length,
                        sizes: scripts.map(script => script.src.length * 100) // Rough estimate
                    };
                """)
                
                resource_analysis['javascript']['total_size'] += sum(js_info.get('sizes', []))
                
                # Analyze fonts
                fonts = driver.execute_script("""
                    const fontLinks = Array.from(document.querySelectorAll('link[href*="font"]'));
                    return fontLinks.length;
                """)
                
                resource_analysis['fonts']['total'] += fonts
                resource_analysis['fonts']['web_fonts'] += fonts
        
        finally:
            driver.quit()
        
        # Generate recommendations
        if resource_analysis['images']['unoptimized'] > 0:
            resource_analysis['images']['recommendations'].extend([
                "Add alt attributes to all images",
                "Implement lazy loading for images",
                "Use modern image formats (WebP, AVIF)",
                "Optimize image sizes and compression"
            ])
        
        if resource_analysis['css']['total_size'] > 50000:  # 50KB
            resource_analysis['css']['recommendations'].extend([
                "Remove unused CSS",
                "Implement critical CSS inlining",
                "Use CSS minification",
                "Consider CSS-in-JS for better tree shaking"
            ])
        
        if resource_analysis['javascript']['total_size'] > 200000:  # 200KB
            resource_analysis['javascript']['recommendations'].extend([
                "Implement code splitting",
                "Remove unused JavaScript",
                "Use dynamic imports",
                "Optimize bundle size with webpack-bundle-analyzer"
            ])
        
        if resource_analysis['fonts']['web_fonts'] > 3:
            resource_analysis['fonts']['recommendations'].extend([
                "Limit number of web fonts",
                "Use font-display: swap",
                "Preload critical fonts",
                "Consider system fonts for better performance"
            ])
        
        return resource_analysis
    
    async def _analyze_rendering(self, base_url: str, tabs: List[Dict[str, str]]) -> Dict[str, Any]:
        """Analyze rendering performance"""
        logger.info("Analyzing rendering performance")
        
        rendering_analysis = {
            'layout_shifts': [],
            'paint_times': [],
            'render_blocking': [],
            'recommendations': []
        }
        
        driver = self._setup_browser()
        
        try:
            for tab in tabs:
                url = f"{base_url}{tab['path']}"
                driver.get(url)
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Get paint timing information
                paint_times = driver.execute_script("""
                    const paintEntries = performance.getEntriesByType('paint');
                    return paintEntries.map(entry => ({
                        name: entry.name,
                        startTime: entry.startTime
                    }));
                """)
                
                rendering_analysis['paint_times'].extend(paint_times)
                
                # Check for render-blocking resources
                render_blocking = driver.execute_script("""
                    const blockingScripts = Array.from(document.querySelectorAll('script:not([async]):not([defer])'));
                    const blockingStyles = Array.from(document.querySelectorAll('link[rel="stylesheet"]:not([media="print"])'));
                    
                    return {
                        blocking_scripts: blockingScripts.length,
                        blocking_styles: blockingStyles.length,
                        total_blocking: blockingScripts.length + blockingStyles.length
                    };
                """)
                
                rendering_analysis['render_blocking'].append(render_blocking)
        
        finally:
            driver.quit()
        
        # Generate recommendations
        total_blocking = sum(rb.get('total_blocking', 0) for rb in rendering_analysis['render_blocking'])
        if total_blocking > 5:
            rendering_analysis['recommendations'].extend([
                "Add async/defer attributes to non-critical scripts",
                "Inline critical CSS",
                "Use resource hints (preload, prefetch)",
                "Implement progressive loading"
            ])
        
        return rendering_analysis
    
    async def _analyze_network(self, base_url: str, tabs: List[Dict[str, str]]) -> Dict[str, Any]:
        """Analyze network performance"""
        logger.info("Analyzing network performance")
        
        network_analysis = {
            'total_requests': 0,
            'failed_requests': 0,
            'total_size': 0,
            'compression_ratio': 0,
            'caching_headers': [],
            'recommendations': []
        }
        
        async with aiohttp.ClientSession() as session:
            for tab in tabs:
                url = f"{base_url}{tab['path']}"
                
                try:
                    async with session.get(url) as response:
                        network_analysis['total_requests'] += 1
                        
                        if response.status >= 400:
                            network_analysis['failed_requests'] += 1
                        
                        content_length = response.headers.get('content-length')
                        if content_length:
                            network_analysis['total_size'] += int(content_length)
                        
                        # Check compression
                        content_encoding = response.headers.get('content-encoding', '')
                        if content_encoding:
                            network_analysis['compression_ratio'] += 1
                        
                        # Check caching headers
                        cache_control = response.headers.get('cache-control', '')
                        etag = response.headers.get('etag', '')
                        
                        if cache_control or etag:
                            network_analysis['caching_headers'].append({
                                'url': url,
                                'cache_control': cache_control,
                                'etag': etag
                            })
                
                except Exception as e:
                    logger.error(f"Failed to analyze network for {url}: {str(e)}")
                    network_analysis['failed_requests'] += 1
        
        # Generate recommendations
        if network_analysis['failed_requests'] > 0:
            network_analysis['recommendations'].append("Fix failed network requests")
        
        if network_analysis['compression_ratio'] < network_analysis['total_requests'] * 0.8:
            network_analysis['recommendations'].append("Enable compression for more resources")
        
        if len(network_analysis['caching_headers']) < network_analysis['total_requests'] * 0.5:
            network_analysis['recommendations'].append("Implement proper caching headers")
        
        return network_analysis
    
    async def _analyze_memory(self, base_url: str, tabs: List[Dict[str, str]]) -> Dict[str, Any]:
        """Analyze memory usage patterns"""
        logger.info("Analyzing memory usage")
        
        memory_analysis = {
            'peak_memory': 0,
            'memory_leaks': [],
            'large_objects': [],
            'recommendations': []
        }
        
        driver = self._setup_browser()
        
        try:
            for tab in tabs:
                url = f"{base_url}{tab['path']}"
                driver.get(url)
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Get memory information
                memory_info = driver.execute_script("""
                    if (performance.memory) {
                        return {
                            used: performance.memory.usedJSHeapSize,
                            total: performance.memory.totalJSHeapSize,
                            limit: performance.memory.jsHeapSizeLimit
                        };
                    }
                    return null;
                """)
                
                if memory_info:
                    memory_analysis['peak_memory'] = max(
                        memory_analysis['peak_memory'],
                        memory_info['used']
                    )
        
        finally:
            driver.quit()
        
        # Generate recommendations
        if memory_analysis['peak_memory'] > 50 * 1024 * 1024:  # 50MB
            memory_analysis['recommendations'].extend([
                "Implement memory cleanup in components",
                "Use weak references where appropriate",
                "Avoid memory leaks in event listeners",
                "Implement virtual scrolling for large lists"
            ])
        
        return memory_analysis
    
    async def _analyze_accessibility(self, base_url: str, tabs: List[Dict[str, str]]) -> Dict[str, Any]:
        """Analyze accessibility performance"""
        logger.info("Analyzing accessibility")
        
        accessibility_analysis = {
            'missing_alt_text': 0,
            'missing_labels': 0,
            'color_contrast_issues': 0,
            'keyboard_navigation_issues': 0,
            'recommendations': []
        }
        
        driver = self._setup_browser()
        
        try:
            for tab in tabs:
                url = f"{base_url}{tab['path']}"
                driver.get(url)
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Check for missing alt text
                images_without_alt = driver.execute_script("""
                    const images = Array.from(document.querySelectorAll('img'));
                    return images.filter(img => !img.alt || img.alt.trim() === '').length;
                """)
                
                accessibility_analysis['missing_alt_text'] += images_without_alt
                
                # Check for missing labels
                inputs_without_labels = driver.execute_script("""
                    const inputs = Array.from(document.querySelectorAll('input, textarea, select'));
                    return inputs.filter(input => {
                        const label = document.querySelector(`label[for="${input.id}"]`);
                        const ariaLabel = input.getAttribute('aria-label');
                        const ariaLabelledBy = input.getAttribute('aria-labelledby');
                        return !label && !ariaLabel && !ariaLabelledBy;
                    }).length;
                """)
                
                accessibility_analysis['missing_labels'] += inputs_without_labels
        
        finally:
            driver.quit()
        
        # Generate recommendations
        if accessibility_analysis['missing_alt_text'] > 0:
            accessibility_analysis['recommendations'].append("Add alt text to all images")
        
        if accessibility_analysis['missing_labels'] > 0:
            accessibility_analysis['recommendations'].append("Add labels to all form inputs")
        
        return accessibility_analysis
    
    async def _analyze_seo(self, base_url: str, tabs: List[Dict[str, str]]) -> Dict[str, Any]:
        """Analyze SEO performance"""
        logger.info("Analyzing SEO performance")
        
        seo_analysis = {
            'missing_titles': 0,
            'missing_meta_descriptions': 0,
            'missing_structured_data': 0,
            'recommendations': []
        }
        
        driver = self._setup_browser()
        
        try:
            for tab in tabs:
                url = f"{base_url}{tab['path']}"
                driver.get(url)
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Check for missing title
                title = driver.execute_script("return document.title;")
                if not title or title.strip() == '':
                    seo_analysis['missing_titles'] += 1
                
                # Check for missing meta description
                meta_description = driver.execute_script("""
                    const meta = document.querySelector('meta[name="description"]');
                    return meta ? meta.content : '';
                """)
                
                if not meta_description or meta_description.strip() == '':
                    seo_analysis['missing_meta_descriptions'] += 1
                
                # Check for structured data
                structured_data = driver.execute_script("""
                    const scripts = Array.from(document.querySelectorAll('script[type="application/ld+json"]'));
                    return scripts.length;
                """)
                
                if structured_data == 0:
                    seo_analysis['missing_structured_data'] += 1
        
        finally:
            driver.quit()
        
        # Generate recommendations
        if seo_analysis['missing_titles'] > 0:
            seo_analysis['recommendations'].append("Add unique, descriptive titles to all pages")
        
        if seo_analysis['missing_meta_descriptions'] > 0:
            seo_analysis['recommendations'].append("Add meta descriptions to all pages")
        
        if seo_analysis['missing_structured_data'] > 0:
            seo_analysis['recommendations'].append("Implement structured data markup")
        
        return seo_analysis
    
    def _setup_browser(self) -> webdriver.Chrome:
        """Setup Chrome browser for analysis"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        return webdriver.Chrome(options=options)
    
    def _generate_comprehensive_recommendations(self, analysis: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Generate comprehensive optimization recommendations"""
        recommendations = []
        
        # Bundle optimization recommendations
        bundle_analysis = analysis.get('bundle_analysis', {})
        if bundle_analysis.get('unused_code_percentage', 0) > 20:
            recommendations.append(OptimizationRecommendation(
                category='Bundle Optimization',
                priority='high',
                title='Remove Unused Code',
                description=f"Remove {bundle_analysis.get('unused_code_percentage', 0):.1f}% of unused code",
                impact='High - Significant bundle size reduction',
                effort='Medium - Requires dependency analysis',
                implementation='Use webpack-bundle-analyzer and remove unused imports',
                expected_improvement='20-40% bundle size reduction'
            ))
        
        # Resource optimization recommendations
        resource_analysis = analysis.get('resource_analysis', {})
        if resource_analysis.get('images', {}).get('unoptimized', 0) > 0:
            recommendations.append(OptimizationRecommendation(
                category='Image Optimization',
                priority='medium',
                title='Optimize Images',
                description='Optimize images for better performance',
                impact='Medium - Faster image loading',
                effort='Low - Automated optimization tools',
                implementation='Use WebP/AVIF formats, implement lazy loading',
                expected_improvement='30-50% image size reduction'
            ))
        
        # Rendering optimization recommendations
        rendering_analysis = analysis.get('rendering_analysis', {})
        if len(rendering_analysis.get('render_blocking', [])) > 0:
            recommendations.append(OptimizationRecommendation(
                category='Rendering Optimization',
                priority='high',
                title='Reduce Render Blocking',
                description='Minimize render-blocking resources',
                impact='High - Faster initial page load',
                effort='Medium - Requires resource prioritization',
                implementation='Inline critical CSS, defer non-critical JS',
                expected_improvement='20-30% faster initial render'
            ))
        
        # Network optimization recommendations
        network_analysis = analysis.get('network_analysis', {})
        if network_analysis.get('compression_ratio', 0) < 0.8:
            recommendations.append(OptimizationRecommendation(
                category='Network Optimization',
                priority='high',
                title='Enable Compression',
                description='Enable gzip/brotli compression',
                impact='High - Reduced transfer size',
                effort='Low - Server configuration',
                implementation='Configure server compression',
                expected_improvement='60-80% size reduction'
            ))
        
        return recommendations
