import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

interface IndianIntelligence {
  city: string;
  state: string;
  address_type: string;
  city_intelligence: any;
  regional_patterns: any;
  risk_assessment: any;
  ecommerce_recommendations: any;
  delivery_success_factors: any;
  logistics_optimization?: {
    hub_recommendations: string[];
    route_optimization_tips: string[];
    cost_factors: {
      fuel_surcharge: string;
      parking_fees: string;
      toll_charges: string;
    };
  };
  weather_impact?: {
    current_conditions: string;
    temperature_celsius: number;
    humidity_percent: number;
    delivery_impact: string;
    recommendations: string[];
  };
  traffic_intelligence?: {
    current_congestion_level: string;
    peak_hours_today: string[];
    alternative_routes_available: boolean;
    estimated_delay_minutes: number;
  };
}

const IndianIntelligenceDemo: React.FC = () => {
  const [selectedCity, setSelectedCity] = useState('Mumbai');
  const [addressType, setAddressType] = useState('residential');
  const [intelligence, setIntelligence] = useState<IndianIntelligence | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Surat', 'Lucknow', 'Kanpur', 'Nagpur', 'Indore', 'Thane', 'Bhopal', 'Visakhapatnam', 'Pimpri-Chinchwad', 'Patna', 'Vadodara'];
  const addressTypes = ['residential', 'commercial', 'industrial'];

  const fetchIntelligence = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        city: selectedCity,
        address_type: addressType,
        include_weather: 'true',
        include_traffic: 'true'
      });
      const response = await api.get(`/indian-intelligence?${params}`);
      setIntelligence(response.data);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to fetch intelligence data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIntelligence();
  }, [selectedCity, addressType]);

  return (
    <div className="min-h-screen bg-[#FAF7F0] p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">India Delivery Intelligence</h1>
          <p className="text-gray-600">AI-powered insights for e-commerce and delivery in Indian cities</p>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Select City</label>
              <select
                value={selectedCity}
                onChange={(e) => setSelectedCity(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {cities.map(city => (
                  <option key={city} value={city}>{city}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Address Type</label>
              <select
                value={addressType}
                onChange={(e) => setAddressType(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {addressTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {loading && (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-gray-600">Loading intelligence data...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {intelligence && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* City Intelligence */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">City Intelligence</h2>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Traffic Multiplier:</span>
                  <span className="font-medium">{intelligence.city_intelligence.traffic_multiplier}x</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Population Density:</span>
                  <span className="font-medium">{intelligence.city_intelligence.population_density}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Autonomous Readiness:</span>
                  <span className="font-medium capitalize">{intelligence.city_intelligence.autonomous_readiness}</span>
                </div>
                <div>
                  <span className="text-gray-600 block mb-1">Delivery Challenges:</span>
                  <div className="flex flex-wrap gap-1">
                    {intelligence.city_intelligence.delivery_challenges.map((challenge: string, idx: number) => (
                      <span key={idx} className="bg-orange-100 text-orange-800 px-2 py-1 rounded text-sm">
                        {challenge}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <span className="text-gray-600 block mb-1">Safety Concerns:</span>
                  <div className="flex flex-wrap gap-1">
                    {intelligence.city_intelligence.safety_concerns.map((concern: string, idx: number) => (
                      <span key={idx} className="bg-red-100 text-red-800 px-2 py-1 rounded text-sm">
                        {concern}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Regional Patterns */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Regional Patterns</h2>
              <div className="space-y-3">
                <div>
                  <span className="text-gray-600 block mb-1">Preferred Delivery Times:</span>
                  <div className="flex flex-wrap gap-1">
                    {intelligence.regional_patterns.preferred_delivery_times.map((time: string, idx: number) => (
                      <span key={idx} className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">
                        {time}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <span className="text-gray-600 block mb-1">Payment Methods:</span>
                  <div className="flex flex-wrap gap-1">
                    {intelligence.regional_patterns.payment_methods.map((method: string, idx: number) => (
                      <span key={idx} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                        {method}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <span className="text-gray-600 block mb-1">Languages:</span>
                  <div className="flex flex-wrap gap-1">
                    {intelligence.regional_patterns.languages.map((lang: string, idx: number) => (
                      <span key={idx} className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-sm">
                        {lang}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Risk Assessment */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Risk Assessment</h2>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Overall Risk:</span>
                  <span className={`font-medium ${intelligence.risk_assessment.overall_risk === 'high' ? 'text-red-600' : intelligence.risk_assessment.overall_risk === 'medium' ? 'text-yellow-600' : 'text-green-600'}`}>
                    {intelligence.risk_assessment.overall_risk.toUpperCase()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Risk Score:</span>
                  <span className="font-medium">{intelligence.risk_assessment.risk_score}/10</span>
                </div>
                <div>
                  <span className="text-gray-600 block mb-1">Risk Factors:</span>
                  <div className="space-y-1">
                    {intelligence.risk_assessment.risk_factors.map((factor: string, idx: number) => (
                      <div key={idx} className="text-sm text-gray-700">• {factor}</div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Logistics Optimization */}
            {intelligence.logistics_optimization && (
              <div className="bg-white rounded-lg shadow-sm p-6 lg:col-span-2">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Logistics Optimization</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Hub Recommendations</h3>
                    <div className="flex flex-wrap gap-1">
                      {intelligence.logistics_optimization.hub_recommendations.map((hub: string, idx: number) => (
                        <span key={idx} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                          {hub}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Route Optimization Tips</h3>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {intelligence.logistics_optimization.route_optimization_tips.map((tip: string, idx: number) => (
                        <li key={idx} className="flex items-start">
                          <span className="text-blue-500 mr-2">•</span>
                          {tip}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Cost Factors</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Fuel Surcharge:</span>
                        <span className="font-medium">{intelligence.logistics_optimization.cost_factors.fuel_surcharge}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Parking Fees:</span>
                        <span className="font-medium">{intelligence.logistics_optimization.cost_factors.parking_fees}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Toll Charges:</span>
                        <span className="font-medium">{intelligence.logistics_optimization.cost_factors.toll_charges}</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Success Rate Estimate</h3>
                    <div className="text-2xl font-bold text-green-600">
                      {intelligence.delivery_success_factors.success_rate_estimate}
                    </div>
                    <p className="text-sm text-gray-600 mt-1">Estimated delivery success rate</p>
                  </div>
                </div>
              </div>
            )}

            {/* Weather Impact */}
            {intelligence.weather_impact && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Weather Impact</h2>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Current Conditions:</span>
                    <span className="font-medium">{intelligence.weather_impact.current_conditions}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Temperature:</span>
                    <span className="font-medium">{intelligence.weather_impact.temperature_celsius}°C</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Humidity:</span>
                    <span className="font-medium">{intelligence.weather_impact.humidity_percent}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Delivery Impact:</span>
                    <span className="font-medium">{intelligence.weather_impact.delivery_impact}</span>
                  </div>
                  <div>
                    <span className="text-gray-600 block mb-1">Recommendations:</span>
                    <div className="flex flex-wrap gap-1">
                      {intelligence.weather_impact.recommendations.map((rec: string, idx: number) => (
                        <span key={idx} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                          {rec}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Traffic Intelligence */}
            {intelligence.traffic_intelligence && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Traffic Intelligence</h2>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Current Congestion:</span>
                    <span className="font-medium">{intelligence.traffic_intelligence.current_congestion_level}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Estimated Delay:</span>
                    <span className="font-medium">{intelligence.traffic_intelligence.estimated_delay_minutes} minutes</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Alternative Routes:</span>
                    <span className="font-medium">{intelligence.traffic_intelligence.alternative_routes_available ? 'Available' : 'Limited'}</span>
                  </div>
                  <div>
                    <span className="text-gray-600 block mb-1">Today's Peak Hours:</span>
                    <div className="flex flex-wrap gap-1">
                      {intelligence.traffic_intelligence.peak_hours_today.map((hour: string, idx: number) => (
                        <span key={idx} className="bg-red-100 text-red-800 px-2 py-1 rounded text-sm">
                          {hour}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* E-commerce Recommendations */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">E-commerce Recommendations</h2>
              <div className="space-y-3">
                <div>
                  <span className="text-gray-600 block mb-1">Vehicle Recommendations:</span>
                  <div className="flex flex-wrap gap-1">
                    {intelligence.ecommerce_recommendations.vehicle_recommendations.map((vehicle: string, idx: number) => (
                      <span key={idx} className="bg-indigo-100 text-indigo-800 px-2 py-1 rounded text-sm">
                        {vehicle}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <span className="text-gray-600 block mb-1">Safety Measures:</span>
                  <div className="flex flex-wrap gap-1">
                    {intelligence.ecommerce_recommendations.safety_measures.map((measure: string, idx: number) => (
                      <span key={idx} className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-sm">
                        {measure}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Autonomous Suitability:</span>
                  <span className="font-medium capitalize">{intelligence.ecommerce_recommendations.autonomous_delivery_suitability}</span>
                </div>
              </div>
            </div>

            {/* Delivery Success Factors */}
            <div className="bg-white rounded-lg shadow-sm p-6 lg:col-span-2">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Delivery Success Factors</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <span className="text-gray-600 block mb-1">Traffic Impact:</span>
                  <p className="font-medium text-red-600">{intelligence.delivery_success_factors.traffic_impact}</p>
                </div>
                <div>
                  <span className="text-gray-600 block mb-1">Estimated Delivery Time:</span>
                  <p className="font-medium">{intelligence.delivery_success_factors.estimated_delivery_time}</p>
                </div>
                <div>
                  <span className="text-gray-600 block mb-1">Peak Hours to Avoid:</span>
                  <div className="flex flex-wrap gap-1">
                    {intelligence.delivery_success_factors.peak_hour_avoidance.map((hour: string, idx: number) => (
                      <span key={idx} className="bg-red-100 text-red-800 px-2 py-1 rounded text-sm">
                        {hour}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <span className="text-gray-600 block mb-1">Local Challenges:</span>
                  <div className="flex flex-wrap gap-1">
                    {intelligence.delivery_success_factors.local_challenges.map((challenge: string, idx: number) => (
                      <span key={idx} className="bg-orange-100 text-orange-800 px-2 py-1 rounded text-sm">
                        {challenge}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default IndianIntelligenceDemo;