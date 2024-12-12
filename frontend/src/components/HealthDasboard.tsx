"use client"

import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import {
    Heart,
    Droplets,
    Activity,
    AlertCircle,
    Timer,
    Compass,
    CarFront,
    PersonStanding,
    Dumbbell
} from 'lucide-react';

const CustomAlert = ({ title, description, icon: Icon }) => (
    <div className="mb-6 bg-red-900/50 border-2 border-red-500 rounded-lg p-4 text-white">
        <div className="flex items-center gap-2 mb-2">
            <Icon className="h-5 w-5 text-red-500" />
            <h3 className="font-semibold">{title}</h3>
        </div>
        <p className="text-gray-300">{description}</p>
    </div>
);

const MetricCard = ({ title, value, unit, icon: Icon, color, warning }) => (
    <div className={`bg-black border-2 ${warning ? 'border-red-500' : 'border-gray-800'} rounded-lg shadow p-6 transition-all duration-300 hover:border-gray-600`}>
        <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-300">{title}</h2>
            <Icon className={`w-6 h-6 text-${color}`} />
        </div>
        <div className="text-3xl font-bold text-white transition-all duration-300">
            {value} {unit}
        </div>
    </div>
);

const SimulationControl = ({ onSimulate }) => (
    <div className="bg-black border-2 border-gray-800 rounded-lg shadow p-6 mb-8">
        <h2 className="text-lg font-semibold text-gray-300 mb-4">Accident Simulation Controls</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <button
                onClick={() => onSimulate('car_crash')}
                className="flex items-center justify-center gap-2 bg-red-900/30 hover:bg-red-900/50 text-red-500 border-2 border-red-900 rounded-lg p-3 transition-all duration-300"
            >
                <CarFront className="w-5 h-5" />
                Simulate Car Crash
            </button>
            <button
                onClick={() => onSimulate('fall')}
                className="flex items-center justify-center gap-2 bg-orange-900/30 hover:bg-orange-900/50 text-orange-500 border-2 border-orange-900 rounded-lg p-3 transition-all duration-300"
            >
                <PersonStanding className="w-5 h-5" />
                Simulate Fall
            </button>
            <button
                onClick={() => onSimulate('sports_injury')}
                className="flex items-center justify-center gap-2 bg-yellow-900/30 hover:bg-yellow-900/50 text-yellow-500 border-2 border-yellow-900 rounded-lg p-3 transition-all duration-300"
            >
                <Dumbbell className="w-5 h-5" />
                Simulate Sports Injury
            </button>
        </div>
    </div>
);

const AccidentAlert = ({ accident }) => (
    <div className="mb-6 bg-red-900/50 border-2 border-red-500 rounded-lg p-4 text-white">
        <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="h-5 w-5 text-red-500" />
            <h3 className="font-semibold">Accident Detected</h3>
        </div>
        <div className="space-y-2">
            <p className="text-gray-300">Type: {accident.accident_type.replace('_', ' ').toUpperCase()}</p>
            <p className="text-gray-300">Phase: {accident.accident_phase.replace('_', ' ')}</p>
            <p className="text-gray-300">Elapsed time: {Math.round(accident.elapsed_time)} seconds</p>
        </div>
    </div>
);

export default function HealthDashboard() {
    const [metrics, setMetrics] = useState(null);
    const [history, setHistory] = useState([]);
    const [lastUpdate, setLastUpdate] = useState(new Date());
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    const simulateAccident = async (type) => {
        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/health/user123/simulate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ accident_type: type }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            fetchMetrics();
        } catch (error) {
            console.error('Error simulating accident:', error);
            setError('Failed to simulate accident');
        }
    };

    const fetchMetrics = async () => {
        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/health/user123`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            setMetrics(data);
            setLastUpdate(new Date());
            setError(null);
        } catch (error) {
            console.error('Error fetching metrics:', error);
            setError('Failed to fetch current metrics');
        } finally {
            setLoading(false);
        }
    };

    const fetchHistory = async () => {
        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/health/user123/history?hours=24`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            setHistory(data);
        } catch (error) {
            console.error('Error fetching history:', error);
        }
    };

    useEffect(() => {
        fetchMetrics();
        fetchHistory();

        const metricsInterval = setInterval(fetchMetrics, 5000);
        const historyInterval = setInterval(fetchHistory, 60000);

        return () => {
            clearInterval(metricsInterval);
            clearInterval(historyInterval);
        };
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-lg text-gray-300 animate-pulse">Loading health metrics...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-red-500 flex items-center gap-2">
                    <AlertCircle className="w-6 h-6" />
                    <span>{error}</span>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6">
            <div className="max-w-7xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-3xl font-bold text-white">Health Monitoring Dashboard</h1>
                    <div className="text-sm text-gray-500">
                        Last updated: {lastUpdate.toLocaleTimeString()}
                    </div>
                </div>

                <SimulationControl onSimulate={simulateAccident} />

                {metrics?.accident_data && (
                    <AccidentAlert accident={metrics.accident_data} />
                )}

                {metrics?.movement_data?.activity_state === 'fallen' &&
                    metrics.movement_data.minutes_since_last_movement > 5 && (
                        <CustomAlert
                            icon={AlertCircle}
                            title="Potential Emergency Detected"
                            description={`No movement detected for ${Math.round(metrics.movement_data.minutes_since_last_movement)} minutes after fall detection.`}
                        />
                    )}

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <MetricCard
                        title="Heart Rate"
                        value={Math.round(metrics.vital_signs.heart_rate)}
                        unit="BPM"
                        icon={Heart}
                        color="red-500"
                        warning={metrics.vital_signs.heart_rate > 120 || metrics.vital_signs.heart_rate < 50}
                    />

                    <MetricCard
                        title="Blood Oxygen"
                        value={Math.round(metrics.vital_signs.spo2)}
                        unit="%"
                        icon={Droplets}
                        color="blue-500"
                        warning={metrics.vital_signs.spo2 < 95}
                    />

                    <MetricCard
                        title="Respiratory Rate"
                        value={Math.round(metrics.vital_signs.respiratory_rate)}
                        unit="/min"
                        icon={Timer}
                        color="teal-500"
                        warning={metrics.vital_signs.respiratory_rate < 12 || metrics.vital_signs.respiratory_rate > 20}
                    />

                    <MetricCard
                        title="Blood Pressure"
                        value={`${Math.round(metrics.vital_signs.blood_pressure.systolic)}/${Math.round(metrics.vital_signs.blood_pressure.diastolic)}`}
                        unit="mmHg"
                        icon={Activity}
                        color="purple-500"
                        warning={metrics.vital_signs.blood_pressure.systolic > 140 || metrics.vital_signs.blood_pressure.systolic < 90}
                    />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    <div className="bg-black border-2 border-gray-800 rounded-lg shadow p-6">
                        <h2 className="text-lg font-semibold text-gray-300 mb-4">Movement Data</h2>
                        <div className="space-y-4 text-white">
                            <div className="flex justify-between">
                                <span className="text-gray-400">Activity State:</span>
                                <span className={metrics.movement_data.activity_state === 'fallen' ? 'text-red-500' : ''}>
                                    {metrics.movement_data.activity_state}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-400">Device Orientation:</span>
                                <span>{metrics.movement_data.device_orientation}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-400">Minutes Since Movement:</span>
                                <span>{Math.round(metrics.movement_data.minutes_since_last_movement)} min</span>
                            </div>
                        </div>
                    </div>

                    <div className="bg-black border-2 border-gray-800 rounded-lg shadow p-6">
                        <h2 className="text-lg font-semibold text-gray-300 mb-4">Location Context</h2>
                        <div className="space-y-4 text-white">
                            <div className="flex justify-between">
                                <span className="text-gray-400">Location Type:</span>
                                <span>{metrics.context.location_type}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-400">GPS Coordinates:</span>
                                <span>
                                    {metrics.context.gps_coordinates.latitude.toFixed(6)},
                                    {metrics.context.gps_coordinates.longitude.toFixed(6)}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-400">Time of Day:</span>
                                <span>{metrics.context.time_of_day}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="bg-black border-2 border-gray-800 rounded-lg shadow p-6">
                    <h2 className="text-lg font-semibold text-gray-300 mb-4">Vital Signs History</h2>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={history}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                <XAxis
                                    dataKey="timestamp"
                                    tick={{ fill: '#9CA3AF' }}
                                    tickFormatter={(timestamp) => new Date(timestamp).toLocaleTimeString()}
                                />
                                <YAxis
                                    tick={{ fill: '#9CA3AF' }}
                                    domain={['dataMin - 5', 'dataMax + 5']}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#111827',
                                        border: '1px solid #374151',
                                        borderRadius: '0.5rem',
                                    }}
                                    labelStyle={{ color: '#9CA3AF' }}
                                    labelFormatter={(timestamp) => new Date(timestamp).toLocaleString()}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="vital_signs.heart_rate"
                                    stroke="#EF4444"
                                    strokeWidth={2}
                                    dot={false}
                                    name="Heart Rate"
                                />
                                <Line
                                    type="monotone"
                                    dataKey="vital_signs.respiratory_rate"
                                    stroke="#2DD4BF"
                                    strokeWidth={2}
                                    dot={false}
                                    name="Respiratory Rate"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
}