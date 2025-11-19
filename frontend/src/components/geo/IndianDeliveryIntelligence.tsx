import React from 'react';
import Card from '../Card';

interface IndianDeliveryIntelligenceProps {
  data: {
    delivery_risk_assessment?: any;
    route_optimization?: any;
  };
}

export const IndianDeliveryIntelligence: React.FC<IndianDeliveryIntelligenceProps> = ({ data }) => {
  if (!data || (!data.delivery_risk_assessment && !data.route_optimization)) {
    return null;
  }

  const risk = data.delivery_risk_assessment;
  const route = data.route_optimization;

  return (
    <div className="space-y-6">
      {/* Risk Assessment Card */}
      {risk && (
        <Card>
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Indian Delivery Intelligence</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Risk Assessment</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Overall Risk:</span>
                      <span className={`font-medium ${risk.overall_risk_score > 0.7 ? 'text-red-600' : risk.overall_risk_score > 0.4 ? 'text-yellow-600' : 'text-green-600'}`}>
                        {risk.overall_risk_score > 0.7 ? 'High' : risk.overall_risk_score > 0.4 ? 'Medium' : 'Low'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Risk Score:</span>
                      <span className="font-medium">{(risk.overall_risk_score * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">City Intelligence</h4>
                  <div className="space-y-1">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Traffic Impact:</span>
                      <span className="font-medium">{((risk.city_intelligence?.traffic_multiplier || 1) - 1) * 100}% slower</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Autonomous Ready:</span>
                      <span className="font-medium capitalize">{risk.city_intelligence?.autonomous_readiness || 'Unknown'}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Risk Factors */}
              {risk.risk_factors && risk.risk_factors.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-medium text-gray-700 mb-2">Risk Factors</h4>
                  <div className="flex flex-wrap gap-2">
                    {risk.risk_factors.map((factor: string, idx: number) => (
                      <span key={idx} className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        {factor.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Delivery Challenges */}
              {risk.city_intelligence?.delivery_challenges && risk.city_intelligence.delivery_challenges.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-medium text-gray-700 mb-2">Delivery Challenges</h4>
                  <div className="flex flex-wrap gap-2">
                    {risk.city_intelligence.delivery_challenges.map((challenge: string, idx: number) => (
                      <span key={idx} className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                        {challenge.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Safety Concerns */}
              {risk.city_intelligence?.safety_concerns && risk.city_intelligence.safety_concerns.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-medium text-gray-700 mb-2">Safety Concerns</h4>
                  <div className="flex flex-wrap gap-2">
                    {risk.city_intelligence.safety_concerns.map((concern: string, idx: number) => (
                      <span key={idx} className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        {concern.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </Card>
      )}

      {/* Route Optimization Card */}
      {route && (
        <Card>
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                </svg>
              </div>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Route Optimization</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Traffic Considerations</h4>
                  <div className="space-y-1">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Traffic Multiplier:</span>
                      <span className="font-medium">{route.traffic_multiplier}x normal time</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Buffer Time:</span>
                      <span className="font-medium">{route.recommended_departure_buffer || 0} min early</span>
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Regional Patterns</h4>
                  <div className="space-y-1">
                    {risk?.regional_patterns?.preferred_delivery_times && (
                      <div>
                        <span className="text-sm text-gray-600">Best Delivery Times:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {risk.regional_patterns.preferred_delivery_times.map((time: string, idx: number) => (
                            <span key={idx} className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
                              {time}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Safety Precautions */}
              {route.safety_precautions && route.safety_precautions.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-medium text-gray-700 mb-2">Safety Precautions</h4>
                  <div className="flex flex-wrap gap-2">
                    {route.safety_precautions.map((precaution: string, idx: number) => (
                      <span key={idx} className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        {precaution.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Vehicle Recommendations */}
              {route.vehicle_recommendations && route.vehicle_recommendations.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-medium text-gray-700 mb-2">Recommended Vehicles</h4>
                  <div className="flex flex-wrap gap-2">
                    {route.vehicle_recommendations.map((vehicle: string, idx: number) => (
                      <span key={idx} className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {vehicle.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};