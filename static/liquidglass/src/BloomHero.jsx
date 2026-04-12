import React, { useEffect, useRef } from 'react';
import {
  Sparkles,
  Download,
  Wand2,
  BookOpen,
  ArrowRight,
  Twitter,
  Linkedin,
  Instagram,
  Menu,
} from 'lucide-react';

export default function BloomHero() {
  const videoRef = useRef(null);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.play().catch(err => console.log('Video play error:', err));
    }
  }, []);

  return (
    <div className="relative w-full min-h-screen overflow-hidden">
      {/* Video Background */}
      <div className="video-container">
        <video
          ref={videoRef}
          className="video-background"
          autoPlay
          muted
          loop
          playsInline
          src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260315_073750_51473149-4350-4920-ae24-c8214286f323.mp4"
        />
      </div>

      {/* Content Overlay */}
      <div className="relative z-10 flex min-h-screen w-full">

        {/* LEFT PANEL */}
        <div className="flex w-full lg:w-[52%] flex-col">
          {/* Navigation */}
          <nav className="flex items-center justify-between px-10 py-6 lg:px-12 lg:py-8">
            {/* Logo Section */}
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                <span className="text-sm font-semibold">B</span>
              </div>
              <span className="text-2xl font-semibold tracking-tighter text-white">bloom</span>
            </div>

            {/* Menu Button */}
            <button className="liquid-glass flex items-center justify-center w-10 h-10 rounded-full interactive">
              <Menu size={20} className="text-white" />
            </button>
          </nav>

          {/* Hero Center Content */}
          <div className="flex-1 flex flex-col items-center justify-center px-6 lg:px-12 text-center">
            {/* Logo */}
            <div className="mb-12">
              <div className="w-20 h-20 bg-white/20 rounded-lg flex items-center justify-center mx-auto">
                <span className="text-3xl font-bold">B</span>
              </div>
            </div>

            {/* Main Heading */}
            <h1 className="font-display text-6xl lg:text-7xl font-medium tracking-[-0.05em] text-white leading-tight mb-8">
              Innovating the <br />
              <span className="italic">
                <span className="font-serif text-white/80">spirit</span>
              </span> of <em className="font-serif text-white/80">bloom</em> AI
            </h1>

            {/* CTA Button */}
            <button className="liquid-glass-ultra flex items-center justify-center gap-3 px-8 py-4 rounded-full mb-12 interactive group">
              <span className="text-white font-medium text-lg">Explore Now</span>
              <div className="w-7 h-7 rounded-full bg-white/15 flex items-center justify-center group-hover:bg-white/20 transition-colors">
                <Download size={18} className="text-white" />
              </div>
            </button>

            {/* Pill Tags */}
            <div className="flex flex-wrap gap-3 justify-center">
              <div className="liquid-glass px-6 py-2 rounded-full interactive">
                <span className="text-xs text-white/80 font-medium">Artistic Gallery</span>
              </div>
              <div className="liquid-glass px-6 py-2 rounded-full interactive">
                <span className="text-xs text-white/80 font-medium">AI Generation</span>
              </div>
              <div className="liquid-glass px-6 py-2 rounded-full interactive">
                <span className="text-xs text-white/80 font-medium">3D Structures</span>
              </div>
            </div>
          </div>

          {/* Bottom Quote Section */}
          <div className="flex flex-col items-center justify-center px-6 lg:px-12 pb-8 lg:pb-12">
            <span className="text-xs tracking-widest uppercase text-white/50 mb-4">
              Visionary Design
            </span>
            <p className="font-serif text-lg lg:text-xl italic text-white/80 mb-6 max-w-md">
              We imagined a realm with no ending.
            </p>
            <div className="flex items-center gap-4 text-white/60 text-xs font-medium tracking-widest">
              <div className="h-px w-8 bg-white/30"></div>
              <span>MARCUS AURELIO</span>
              <div className="h-px w-8 bg-white/30"></div>
            </div>
          </div>
        </div>

        {/* RIGHT PANEL (Desktop Only) */}
        <div className="hidden lg:flex w-[48%] flex-col px-8 py-8">
          {/* Top Bar */}
          <div className="flex items-center justify-between gap-3 mb-8">
            {/* Social Icons */}
            <div className="liquid-glass-ultra flex items-center gap-3 px-4 py-3 rounded-full">
              <button className="icon-container text-white hover:text-white/80 transition-colors interactive">
                <Twitter size={18} />
              </button>
              <button className="icon-container text-white hover:text-white/80 transition-colors interactive">
                <Linkedin size={18} />
              </button>
              <button className="icon-container text-white hover:text-white/80 transition-colors interactive">
                <Instagram size={18} />
              </button>
              <div className="w-px h-5 bg-white/20"></div>
              <button className="icon-container text-white hover:text-white/80 transition-colors interactive">
                <ArrowRight size={18} />
              </button>
            </div>

            {/* Account Button */}
            <button className="liquid-glass flex items-center justify-center w-12 h-12 rounded-full interactive">
              <Sparkles size={20} className="text-white" />
            </button>
          </div>

          {/* Community Card */}
          <div className="liquid-glass-ultra px-6 py-6 rounded-3xl mb-8 interactive">
            <h3 className="text-sm font-semibold text-white mb-2">
              Enter our ecosystem
            </h3>
            <p className="text-xs text-white/60">
              Join a community of designers and plant enthusiasts
            </p>
          </div>

          {/* Bottom Feature Section */}
          <div className="mt-auto">
            <div className="liquid-glass-ultra rounded-[2.5rem] p-6 space-y-4">
              {/* Two Side-by-Side Cards */}
              <div className="grid grid-cols-2 gap-4">
                {/* Processing Card */}
                <div className="liquid-glass-ultra rounded-3xl p-4 flex flex-col items-center justify-center text-center interactive">
                  <div className="w-10 h-10 rounded-full bg-white/15 flex items-center justify-center mb-3">
                    <Wand2 size={20} className="text-white/80" />
                  </div>
                  <span className="text-xs font-medium text-white">Processing</span>
                </div>

                {/* Growth Archive Card */}
                <div className="liquid-glass-ultra rounded-3xl p-4 flex flex-col items-center justify-center text-center interactive">
                  <div className="w-10 h-10 rounded-full bg-white/15 flex items-center justify-center mb-3">
                    <BookOpen size={20} className="text-white/80" />
                  </div>
                  <span className="text-xs font-medium text-white">Growth Archive</span>
                </div>
              </div>

              {/* Bottom Feature Card */}
              <div className="liquid-glass-ultra rounded-3xl p-4">
                {/* Flower Image Thumbnail */}
                <div className="w-full h-16 bg-white/10 rounded-2xl mb-3 flex items-center justify-center">
                  <span className="text-xs text-white/50">Flower Image</span>
                </div>
                <h4 className="text-xs font-semibold text-white mb-1">
                  Advanced Plant Sculpting
                </h4>
                <p className="text-xs text-white/60 mb-3">
                  Precision 3D modeling for botanical design
                </p>
                <button className="liquid-glass flex items-center justify-center w-8 h-8 rounded-full mx-auto interactive">
                  <span className="text-white text-lg">+</span>
                </button>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
