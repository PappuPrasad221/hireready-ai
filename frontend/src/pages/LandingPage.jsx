import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Brain, Mic, Camera, BarChart3, Sparkles, ArrowRight, CheckCircle, Users, Target, Zap } from 'lucide-react'

const LandingPage = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY })
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  const features = [
    {
      icon: <Brain className="w-6 h-6" />,
      title: "AI-Powered Questions",
      description: "Dynamic questions tailored to your resume and target role"
    },
    {
      icon: <Mic className="w-6 h-6" />,
      title: "Voice Interviews",
      description: "Natural conversation without typing - just speak your answers"
    },
    {
      icon: <Camera className="w-6 h-6" />,
      title: "Behavior Tracking",
      description: "AI analyzes eye contact, attention, and engagement levels"
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: "Detailed Analytics",
      description: "Comprehensive feedback with actionable improvement tips"
    }
  ]

  const stats = [
    { value: "10K+", label: "Users Trained" },
    { value: "95%", label: "Success Rate" },
    { value: "500+", label: "Companies" },
    { value: "4.9/5", label: "User Rating" }
  ]

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 bg-gradient-to-br from-dark-bg via-dark-surface to-dark-bg">
        <div 
          className="absolute inset-0 opacity-30"
          style={{
            background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(0, 212, 255, 0.1) 0%, transparent 50%)`
          }}
        />
        <div className="absolute inset-0">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="absolute rounded-full bg-neon-blue opacity-10 animate-pulse-slow"
              style={{
                width: Math.random() * 100 + 50 + 'px',
                height: Math.random() * 100 + 50 + 'px',
                left: Math.random() * 100 + '%',
                top: Math.random() * 100 + '%',
                animationDelay: Math.random() * 5 + 's',
                animationDuration: Math.random() * 10 + 10 + 's'
              }}
            />
          ))}
        </div>
      </div>

      {/* Navigation */}
      <nav className="relative z-10 glass-card mx-4 mt-4 px-8 py-4 rounded-2xl">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <Brain className="w-8 h-8 text-neon-blue" />
            <span className="text-2xl font-bold text-gradient">HireReady AI</span>
          </div>
          <div className="flex space-x-6">
            <Link to="/dashboard" className="text-gray-300 hover:text-white transition-colors">Dashboard</Link>
            <Link to="/resume" className="btn-secondary">Get Started</Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 container mx-auto px-4 pt-20 pb-32">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-4xl mx-auto"
        >
          <motion.div
            className="inline-flex items-center space-x-2 glass-card px-6 py-3 rounded-full mb-8"
            whileHover={{ scale: 1.05 }}
          >
            <Sparkles className="w-5 h-5 text-neon-cyan" />
            <span className="text-neon-cyan">AI-Powered Interview Training</span>
          </motion.div>

          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            <span className="text-gradient">Crack Interviews</span>
            <br />
            <span className="text-white">with AI</span>
          </h1>

          <p className="text-xl text-gray-300 mb-12 max-w-2xl mx-auto">
            Practice real interviews with AI that analyzes your voice, facial expressions, and answers. 
            Get personalized feedback to land your dream job.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/resume" className="btn-primary text-lg">
              Start Interview
              <ArrowRight className="w-5 h-5 ml-2" />
            </Link>
            <button className="btn-secondary text-lg">
              Watch Demo
            </button>
          </div>
        </motion.div>

        {/* Animated AI Brain */}
        <motion.div
          className="mt-16 flex justify-center"
          animate={{ rotate: 360 }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
        >
          <div className="relative">
            <Brain className="w-32 h-32 text-neon-blue opacity-20" />
            <Brain className="w-32 h-32 text-neon-purple absolute top-0 left-0 animate-pulse" />
          </div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="relative z-10 container mx-auto px-4 py-20">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl font-bold text-gradient mb-4">
            Revolutionary Interview Training
          </h2>
          <p className="text-gray-300 text-lg max-w-2xl mx-auto">
            Our AI system goes beyond traditional mock interviews with real-time behavioral analysis
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              whileHover={{ y: -10, scale: 1.02 }}
              className="glass-card p-6 group cursor-pointer"
            >
              <div className="w-12 h-12 rounded-full bg-gradient-to-r from-neon-blue to-neon-purple flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                {feature.icon}
              </div>
              <h3 className="text-xl font-semibold mb-3 text-white">{feature.title}</h3>
              <p className="text-gray-400">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Stats Section */}
      <section className="relative z-10 container mx-auto px-4 py-20">
        <div className="glass-card p-12 rounded-3xl">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.5 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="text-center"
              >
                <div className="text-3xl md:text-4xl font-bold text-gradient mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-400">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 container mx-auto px-4 py-20">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
          className="glass-card p-12 rounded-3xl text-center bg-gradient-to-r from-neon-blue/10 to-neon-purple/10"
        >
          <Target className="w-16 h-16 text-neon-cyan mx-auto mb-6" />
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Ace Your Next Interview?
          </h2>
          <p className="text-gray-300 mb-8 max-w-2xl mx-auto">
            Join thousands of professionals who've transformed their interview skills with AI
          </p>
          <Link to="/resume" className="btn-primary text-lg">
            Start Training Now
            <Zap className="w-5 h-5 ml-2" />
          </Link>
        </motion.div>
      </section>
    </div>
  )
}

export default LandingPage
