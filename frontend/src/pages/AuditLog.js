import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import config from '../config';
import { toast } from 'react-hot-toast';

const AuditLog = () => {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filters, setFilters] = useState({
        action: '',
        resource_type: '',
        user: ''
    });
    const [dateRange, setDateRange] = useState({
        start: '',
        end: ''
    });
    const [viewMode, setViewMode] = useState('table'); // 'table' or 'timeline'
    const [selectedLog, setSelectedLog] = useState(null);

    useEffect(() => {
        fetchLogs();
    }, []);

    const fetchLogs = async () => {
        try {
            const response = await axios.get(`${config.API_URL}/audit`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            setLogs(response.data);
        } catch (error) {
            console.error('Error fetching audit logs:', error);
            toast.error('Failed to load audit logs');
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (isoString) => {
        return new Date(isoString).toLocaleString();
    };

    const getActionIcon = (action) => {
        switch (action) {
            case 'CREATE':
                return (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                );
            case 'UPDATE':
                return (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                );
            case 'DELETE':
                return (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                );
            default:
                return null;
        }
    };

    const getActionColor = (action) => {
        switch (action) {
            case 'CREATE':
                return 'bg-green-100 text-green-800 border-green-200';
            case 'UPDATE':
                return 'bg-blue-100 text-blue-800 border-blue-200';
            case 'DELETE':
                return 'bg-red-100 text-red-800 border-red-200';
            default:
                return 'bg-gray-100 text-gray-800 border-gray-200';
        }
    };

    // Get unique values for filters
    const uniqueUsers = useMemo(() => {
        return [...new Set(logs.map(log => log.user_name))];
    }, [logs]);

    const uniqueResourceTypes = useMemo(() => {
        return [...new Set(logs.map(log => log.resource_type))];
    }, [logs]);

    // Filter logs
    const filteredLogs = useMemo(() => {
        return logs.filter(log => {
            const matchesSearch = !searchTerm ||
                log.resource_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
                log.user_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                log.resource_id.toString().includes(searchTerm);

            const matchesAction = !filters.action || log.action === filters.action;
            const matchesResourceType = !filters.resource_type || log.resource_type === filters.resource_type;
            const matchesUser = !filters.user || log.user_name === filters.user;

            const matchesDateRange = (!dateRange.start || new Date(log.timestamp) >= new Date(dateRange.start)) &&
                (!dateRange.end || new Date(log.timestamp) <= new Date(dateRange.end));

            return matchesSearch && matchesAction && matchesResourceType && matchesUser && matchesDateRange;
        });
    }, [logs, searchTerm, filters, dateRange]);

    // Calculate statistics
    const stats = useMemo(() => {
        return {
            total: filteredLogs.length,
            creates: filteredLogs.filter(l => l.action === 'CREATE').length,
            updates: filteredLogs.filter(l => l.action === 'UPDATE').length,
            deletes: filteredLogs.filter(l => l.action === 'DELETE').length
        };
    }, [filteredLogs]);

    if (loading) {
        return (
            <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    {[...Array(4)].map((_, i) => (
                        <div key={i} className="bg-white rounded-xl shadow-lg p-6 animate-pulse">
                            <div className="h-4 bg-gray-200 rounded w-20 mb-2"></div>
                            <div className="h-8 bg-gray-200 rounded w-12"></div>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-fadeIn">
            {/* Page Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-800">Audit Log</h1>
                    <p className="text-gray-600 mt-1">Complete history of all system activities</p>
                </div>
                <div className="flex items-center space-x-3">
                    <div className="flex bg-gray-100 rounded-lg p-1">
                        <button
                            onClick={() => setViewMode('table')}
                            className={`px-4 py-2 rounded-md transition ${
                                viewMode === 'table'
                                    ? 'bg-white shadow text-blue-600'
                                    : 'text-gray-600 hover:text-gray-900'
                            }`}
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                        </button>
                        <button
                            onClick={() => setViewMode('timeline')}
                            className={`px-4 py-2 rounded-md transition ${
                                viewMode === 'timeline'
                                    ? 'bg-white shadow text-blue-600'
                                    : 'text-gray-600 hover:text-gray-900'
                            }`}
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </button>
                    </div>
                    <button
                        onClick={fetchLogs}
                        className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition transform hover:scale-105"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        <span>Refresh</span>
                    </button>
                </div>
            </div>

            {/* Statistics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
                    <div className="flex items-center justify-between mb-2">
                        <p className="text-blue-100 text-sm font-medium">Total Events</p>
                        <svg className="w-8 h-8 text-blue-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                    </div>
                    <p className="text-3xl font-bold">{stats.total}</p>
                </div>

                <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
                    <div className="flex items-center justify-between mb-2">
                        <p className="text-green-100 text-sm font-medium">Created</p>
                        <svg className="w-8 h-8 text-green-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                        </svg>
                    </div>
                    <p className="text-3xl font-bold">{stats.creates}</p>
                </div>

                <div className="bg-gradient-to-br from-blue-400 to-blue-500 rounded-xl shadow-lg p-6 text-white">
                    <div className="flex items-center justify-between mb-2">
                        <p className="text-blue-100 text-sm font-medium">Updated</p>
                        <svg className="w-8 h-8 text-blue-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                    </div>
                    <p className="text-3xl font-bold">{stats.updates}</p>
                </div>

                <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-xl shadow-lg p-6 text-white">
                    <div className="flex items-center justify-between mb-2">
                        <p className="text-red-100 text-sm font-medium">Deleted</p>
                        <svg className="w-8 h-8 text-red-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                    </div>
                    <p className="text-3xl font-bold">{stats.deletes}</p>
                </div>
            </div>

            {/* Filters */}
            <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                    <svg className="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                    </svg>
                    Filters & Search
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {/* Search */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                </svg>
                            </div>
                            <input
                                type="text"
                                placeholder="Search logs..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                            />
                        </div>
                    </div>

                    {/* Action Filter */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Action</label>
                        <select
                            value={filters.action}
                            onChange={(e) => setFilters(prev => ({ ...prev, action: e.target.value }))}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                        >
                            <option value="">All Actions</option>
                            <option value="CREATE">Create</option>
                            <option value="UPDATE">Update</option>
                            <option value="DELETE">Delete</option>
                        </select>
                    </div>

                    {/* Resource Type Filter */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Resource Type</label>
                        <select
                            value={filters.resource_type}
                            onChange={(e) => setFilters(prev => ({ ...prev, resource_type: e.target.value }))}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                        >
                            <option value="">All Resources</option>
                            {uniqueResourceTypes.map(type => (
                                <option key={type} value={type}>{type}</option>
                            ))}
                        </select>
                    </div>

                    {/* User Filter */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">User</label>
                        <select
                            value={filters.user}
                            onChange={(e) => setFilters(prev => ({ ...prev, user: e.target.value }))}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                        >
                            <option value="">All Users</option>
                            {uniqueUsers.map(user => (
                                <option key={user} value={user}>{user}</option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Date Range */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
                        <input
                            type="datetime-local"
                            value={dateRange.start}
                            onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">End Date</label>
                        <input
                            type="datetime-local"
                            value={dateRange.end}
                            onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                        />
                    </div>
                </div>

                {/* Clear Filters */}
                {(searchTerm || filters.action || filters.resource_type || filters.user || dateRange.start || dateRange.end) && (
                    <div className="mt-4">
                        <button
                            onClick={() => {
                                setSearchTerm('');
                                setFilters({ action: '', resource_type: '', user: '' });
                                setDateRange({ start: '', end: '' });
                            }}
                            className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 px-4 py-2 rounded-lg transition"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                            <span>Clear All Filters</span>
                        </button>
                    </div>
                )}
            </div>

            {/* Table View */}
            {viewMode === 'table' && (
                <div className="bg-white rounded-xl shadow-lg overflow-hidden">
                    <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100">
                        <div className="flex items-center justify-between">
                            <h3 className="text-lg font-semibold text-gray-800">Audit Events</h3>
                            <span className="px-3 py-1 bg-blue-100 text-blue-600 rounded-full text-sm font-medium">
                                {filteredLogs.length} events
                            </span>
                        </div>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="min-w-full">
                            <thead className="bg-gray-50 border-b border-gray-200">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Time</th>
                                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Action</th>
                                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Resource</th>
                                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">User</th>
                                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Changes</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {filteredLogs.map((log) => (
                                    <tr 
                                        key={log.id} 
                                        className="hover:bg-blue-50 transition-all cursor-pointer"
                                        onClick={() => setSelectedLog(log)}
                                    >
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                            {formatDate(log.timestamp)}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getActionColor(log.action)}`}>
                                                {getActionIcon(log.action)}
                                                <span className="ml-1">{log.action}</span>
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center">
                                                <span className="text-sm font-medium text-gray-900">{log.resource_type}</span>
                                                <span className="ml-2 text-sm text-gray-500">#{log.resource_id}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className="inline-flex items-center px-2 py-1 rounded-md bg-gray-100 text-gray-700 text-xs font-medium">
                                                <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                                </svg>
                                                {log.user_name}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            {log.changes ? (
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setSelectedLog(log);
                                                    }}
                                                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                                                >
                                                    View Details →
                                                </button>
                                            ) : (
                                                <span className="text-gray-400 text-sm italic">No changes</span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>

                        {filteredLogs.length === 0 && (
                            <div className="text-center py-12">
                                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                                <p className="mt-2 text-sm text-gray-500">No audit logs found</p>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Timeline View */}
            {viewMode === 'timeline' && (
                <div className="bg-white rounded-xl shadow-lg p-6">
                    <div className="space-y-6">
                        {filteredLogs.length > 0 ? (
                            filteredLogs.map((log, index) => (
                                <div key={log.id} className="relative pl-10 pb-6 last:pb-0">
                                    {/* Timeline line */}
                                    {index !== filteredLogs.length - 1 && (
                                        <div className="absolute left-4 top-6 bottom-0 w-0.5 bg-gray-200"></div>
                                    )}
                                    
                                    {/* Timeline dot */}
                                    <div className={`absolute left-0 top-1 w-8 h-8 rounded-full border-4 border-white ${
                                        log.action === 'CREATE' ? 'bg-green-500' :
                                        log.action === 'UPDATE' ? 'bg-blue-500' :
                                        'bg-red-500'
                                    } flex items-center justify-center`}>
                                        <div className="text-white">
                                            {getActionIcon(log.action)}
                                        </div>
                                    </div>

                                    {/* Content */}
                                    <div className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition cursor-pointer" onClick={() => setSelectedLog(log)}>
                                        <div className="flex items-start justify-between">
                                            <div className="flex-1">
                                                <div className="flex items-center space-x-2 mb-1">
                                                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getActionColor(log.action)}`}>
                                                        {log.action}
                                                    </span>
                                                    <span className="text-sm font-medium text-gray-900">{log.resource_type}</span>
                                                    <span className="text-sm text-gray-500">#{log.resource_id}</span>
                                                </div>
                                                <div className="flex items-center space-x-4 text-xs text-gray-600">
                                                    <span className="flex items-center">
                                                        <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                                        </svg>
                                                        {log.user_name}
                                                    </span>
                                                    <span className="flex items-center">
                                                        <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                                        </svg>
                                                        {formatDate(log.timestamp)}
                                                    </span>
                                                </div>
                                            </div>
                                            {log.changes && (
                                                <button className="text-blue-600 hover:text-blue-800 text-xs font-medium">
                                                    Details →
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="text-center py-12">
                                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <p className="mt-2 text-sm text-gray-500">No events in timeline</p>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Detail Modal */}
            {selectedLog && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-fadeIn">
                    <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden transform transition-all animate-slideIn">
                        <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-3">
                                    <div className={`p-3 rounded-lg ${
                                        selectedLog.action === 'CREATE' ? 'bg-green-100 text-green-600' :
                                        selectedLog.action === 'UPDATE' ? 'bg-blue-100 text-blue-600' :
                                        'bg-red-100 text-red-600'
                                    }`}>
                                        {getActionIcon(selectedLog.action)}
                                    </div>
                                    <div>
                                        <h2 className="text-2xl font-bold text-gray-800">Audit Event Details</h2>
                                        <p className="text-sm text-gray-600">Event #{selectedLog.id}</p>
                                    </div>
                                </div>
                                <button
                                    onClick={() => setSelectedLog(null)}
                                    className="text-gray-400 hover:text-gray-600 transition"
                                >
                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>
                        </div>

                        <div className="p-6 overflow-y-auto max-h-[calc(90vh-180px)]">
                            <div className="space-y-4">
                                {/* Basic Info */}
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-gray-50 rounded-lg p-4">
                                        <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Action</p>
                                        <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-sm font-medium ${getActionColor(selectedLog.action)}`}>
                                            {selectedLog.action}
                                        </span>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-4">
                                        <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Resource</p>
                                        <p className="text-sm font-semibold text-gray-900">
                                            {selectedLog.resource_type} #{selectedLog.resource_id}
                                        </p>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-4">
                                        <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">User</p>
                                        <div className="flex items-center space-x-2">
                                            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                            </svg>
                                            <p className="text-sm font-semibold text-gray-900">{selectedLog.user_name}</p>
                                        </div>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-4">
                                        <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Timestamp</p>
                                        <div className="flex items-center space-x-2">
                                            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                            <p className="text-sm font-semibold text-gray-900">{formatDate(selectedLog.timestamp)}</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Changes */}
                                {selectedLog.changes && (
                                    <div className="bg-gray-50 rounded-lg p-4">
                                        <div className="flex items-center mb-3">
                                            <svg className="w-5 h-5 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                                            </svg>
                                            <h3 className="text-lg font-semibold text-gray-800">Changes</h3>
                                        </div>
                                        <div className="bg-white rounded-lg p-4 border border-gray-200">
                                            <pre className="text-sm text-gray-700 whitespace-pre-wrap overflow-x-auto">
                                                {JSON.stringify(selectedLog.changes, null, 2)}
                                            </pre>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="p-6 border-t border-gray-200 bg-gray-50">
                            <button
                                onClick={() => setSelectedLog(null)}
                                className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition transform hover:scale-105 active:scale-95"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AuditLog;