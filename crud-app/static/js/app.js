document.addEventListener('DOMContentLoaded', () => {

    // Toast Helper
    const showToast = (message, type = 'info') => {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) return;

        const bgClass = type === 'error' ? 'bg-danger' :
            type === 'success' ? 'bg-success' :
                'bg-primary';

        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
        toast.show();

        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    };

    // --- Authentication Logic ---
    const checkAuth = () => {
        const token = localStorage.getItem('token');
        const userName = localStorage.getItem('userName');

        const navLogin = document.getElementById('nav-login');
        const navRegister = document.getElementById('nav-register');
        const navUser = document.getElementById('nav-user');
        const userNameDisplay = document.getElementById('user-name-display');

        if (token) {
            if (navLogin) navLogin.classList.add('d-none');
            if (navRegister) navRegister.classList.add('d-none');
            if (navUser) navUser.classList.remove('d-none');
            if (userName && userNameDisplay) userNameDisplay.textContent = userName;
        } else {
            if (navLogin) navLogin.classList.remove('d-none');
            if (navRegister) navRegister.classList.remove('d-none');
            if (navUser) navUser.classList.add('d-none');
        }
    };

    // Initial check
    checkAuth();

    // Login Handler
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;
            const btn = loginForm.querySelector('button');

            try {
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';

                // OAuth2PasswordRequestForm expects form-urlencoded
                const formData = new URLSearchParams();
                formData.append('username', email);
                formData.append('password', password);

                const response = await fetch('/api/users/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: formData
                });

                if (!response.ok) {
                    const err = await response.json();
                    throw new Error(err.detail || 'Login failed');
                }

                const data = await response.json();
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('userName', data.user_name);
                localStorage.setItem('userId', data.user_id);

                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
                modal.hide();

                // Reset form
                loginForm.reset();

                // Update UI
                checkAuth();
                showToast(`Welcome back, ${data.user_name}!`, 'success');

            } catch (error) {
                showToast(error.message, 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = 'Login';
            }
        });
    }

    // Register Handler
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('register-name').value;
            const email = document.getElementById('register-email').value;
            const password = document.getElementById('register-password').value;
            const btn = registerForm.querySelector('button');

            try {
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Registering...';

                const response = await fetch('/api/users', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, password })
                });

                if (!response.ok) {
                    const err = await response.json();
                    throw new Error(err.detail || 'Registration failed');
                }

                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
                modal.hide();

                registerForm.reset();
                showToast('Registration successful! Please login.', 'success');

                // Open login modal
                new bootstrap.Modal(document.getElementById('loginModal')).show();

            } catch (error) {
                showToast(error.message, 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = 'Register';
            }
        });
    }

    // Logout Handler
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('token');
            localStorage.removeItem('userName');
            localStorage.removeItem('userId');
            checkAuth();
            showToast('Logged out successfully.', 'info');
            // Reload to clear sensitive state if needed
            setTimeout(() => window.location.reload(), 1500);
        });
    }

    // Flight Search Logic
    const flightForm = document.getElementById('flight-search-form');
    const flightResults = document.getElementById('flight-results');

    if (flightForm) {
        flightForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const origin = document.getElementById('origin').value;
            const destination = document.getElementById('destination').value;
            const date = document.getElementById('date').value;

            flightResults.innerHTML = '<div class="text-center w-100"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">Searching flights...</p></div>';

            try {
                const response = await fetch(`/api/travel/flights?origin=${origin}&destination=${destination}&departure_date=${date}`);
                const data = await response.json();

                flightResults.innerHTML = '';

                if (data.error) {
                    flightResults.innerHTML = `<div class="alert alert-danger w-100">${data.error}</div>`;
                    return;
                }

                if (!data.flights || data.flights.length === 0) {
                    const originName = data.origin ? `${data.origin.name} (${data.origin.iataCode})` : 'Origin';
                    const destName = data.destination ? `${data.destination.name} (${data.destination.iataCode})` : 'Destination';
                    flightResults.innerHTML = `<div class="alert alert-info w-100">No flights found from <strong>${originName}</strong> to <strong>${destName}</strong> for this date. <br>Try changing the date or using IATA codes (e.g., BLR, MAA).</div>`;
                    return;
                }

                // Render Flights
                data.flights.slice(0, 6).forEach(flight => {
                    const price = flight.price.total;
                    const currency = flight.price.currency;
                    const airline = flight.airlines[0] || 'Unknown Airline';

                    // Simple logic to get first segment details
                    const itinerary = flight.itineraries[0];
                    const firstSeg = itinerary.segments[0];
                    const lastSeg = itinerary.segments[itinerary.segments.length - 1];

                    const departureTime = new Date(firstSeg.departure.at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                    const arrivalTime = new Date(lastSeg.arrival.at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                    const duration = itinerary.duration.replace('PT', '').toLowerCase();

                    const card = `
                        <div class="col-md-4">
                            <div class="card card-result h-100 p-3 rounded-4">
                                <div class="card-body">
                                    <h5 class="card-title fw-bold text-primary">${airline}</h5>
                                    <div class="d-flex justify-content-between align-items-center mb-3">
                                        <div>
                                            <div class="h4 mb-0">${departureTime}</div>
                                            <small class="text-muted">${firstSeg.departure.iataCode}</small>
                                        </div>
                                        <div class="text-center text-muted">
                                            <i class="fas fa-plane"></i><br>
                                            <small>${duration}</small>
                                        </div>
                                        <div class="text-end">
                                            <div class="h4 mb-0">${arrivalTime}</div>
                                            <small class="text-muted">${lastSeg.arrival.iataCode}</small>
                                        </div>
                                    </div>
                                    <div class="d-flex justify-content-between align-items-center pt-3 border-top border-secondary">
                                        <span class="h5 fw-bold text-white">${currency} ${price}</span>
                                        <button class="btn btn-sm btn-outline-light" onclick="selectFlight('${airline}', '${price}', '${currency}', '${firstSeg.departure.iataCode}', '${lastSeg.arrival.iataCode}', '${date}')">Select</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    flightResults.insertAdjacentHTML('beforeend', card);
                });
            } catch (error) {
                console.error('Error:', error);
                flightResults.innerHTML = `<div class="alert alert-danger w-100">An error occurred while fetching flights.</div>`;
            }
        });
    }

    // Global function for selection
    window.selectFlight = (airline, price, currency, origin, destination, date) => {
        // Populate Trip Planner
        const planDestInput = document.getElementById('plan-destination');
        const planOriginInput = document.getElementById('plan-origin');

        if (planDestInput) planDestInput.value = destination;
        if (planOriginInput) planOriginInput.value = origin;

        // Show notification (custom toast)
        if (typeof showToast === 'function') {
            showToast(`Flight Selected! ${origin} -> ${destination}. Proceeding to Trip Planner...`, 'success');
        } else {
            // Fallback if showToast logic isn't loaded yet for some reason, though it should be
            alert(`Flight Selected! Proceeding to Trip Planner...`);
        }

        setTimeout(() => {
            document.getElementById('planner').scrollIntoView({ behavior: 'smooth' });
        }, 1500);
    };

    // Google Maps URL Generator (Global Helper)
    window.generateGoogleMapsUrl = (itinerary, finalDestination) => {
        let waypoints = [];

        if (Array.isArray(itinerary)) {
            itinerary.forEach(day => {
                if (day.activities) {
                    day.activities.forEach(act => {
                        let point = '';
                        if (typeof act === 'string') {
                            // Filter out logistical steps using includes for robustness
                            if (act.includes('Travel:') || act.includes('Return:') || act.includes('Depart') || act.includes('→')) {
                                return; // Skip
                            }
                            point = act;
                        } else {
                            point = act.attraction && act.attraction.name ? act.attraction.name : (act.description || '');
                        }
                        if (point) {
                            // Append destination city to ensure map accuracy (avoids wrong country matches)
                            if (finalDestination && !point.toLowerCase().includes(finalDestination.toLowerCase())) {
                                point += `, ${finalDestination}`;
                            }
                            waypoints.push(encodeURIComponent(point));
                        }
                    });
                }
            });
        }

        // Remove duplicates
        waypoints = [...new Set(waypoints)];

        let url = 'https://www.google.com/maps/dir/';
        if (waypoints.length > 0) {
            url += waypoints.join('/') + '/';
        }
        if (finalDestination) {
            url += encodeURIComponent(finalDestination);
        }
        return url;
    };

    window.generateOSMUrl = (itinerary, finalDestination) => {
        // Find first and last valid coordinates to define route
        let startCoords = null;
        let endCoords = null;

        if (Array.isArray(itinerary)) {
            for (const day of itinerary) {
                if (day.activities) {
                    for (const act of day.activities) {
                        if (typeof act === 'object' && act.attraction && act.attraction.coordinates) {
                            if (!startCoords) startCoords = act.attraction.coordinates;
                            endCoords = act.attraction.coordinates;
                        }
                    }
                }
            }
        }

        if (startCoords && endCoords) {
            // OSRM / OpenStreetMap Directions format
            // engine=fossgis_osrm_car or graphhopper_car
            return `https://www.openstreetmap.org/directions?engine=fossgis_osrm_car&route=${startCoords.latitude}%2C${startCoords.longitude}%3B${endCoords.latitude}%2C${endCoords.longitude}`;
        }

        // Fallback: Search for destination
        return `https://www.openstreetmap.org/search?query=${encodeURIComponent(finalDestination)}`;
    };

    // Activity Details Modal
    window.showActivityDetails = (activity) => {
        const attr = activity.attraction;
        if (!attr) return;

        // Create modal if it doesn't exist
        let modalEl = document.getElementById('activityDetailModal');
        if (!modalEl) {
            const modalHtml = `
                <div class="modal fade" id="activityDetailModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-dialog-centered modal-lg">
                        <div class="modal-content glass-card border-0">
                            <div class="modal-header border-0 pb-0">
                                <h5 class="modal-title fw-bold text-white" id="activityDetailTitle"></h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body p-0" id="activityDetailBody">
                                <!-- Content injected dynamically -->
                            </div>
                        </div>
                    </div>
                </div>`;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            modalEl = document.getElementById('activityDetailModal');
        }

        // Populate modal content
        document.getElementById('activityDetailTitle').textContent = attr.name || 'Activity Details';

        const bodyEl = document.getElementById('activityDetailBody');

        // Build content
        let content = '';

        // Hero Image
        if (attr.image) {
            content += `
                <div class="position-relative" style="height: 300px; overflow: hidden;">
                    <img src="${attr.image}" class="w-100 h-100 object-fit-cover" alt="${attr.name}" 
                         style="object-position: center;" onerror="this.parentElement.style.display='none'">
                    <div class="position-absolute bottom-0 start-0 end-0 p-3" 
                         style="background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);">
                        <span class="badge bg-primary px-3 py-2">${activity.time || ''}</span>
                    </div>
                </div>`;
        }

        // Content section
        content += `<div class="p-4">`;

        // Description
        if (attr.description) {
            content += `
                <div class="mb-3">
                    <h6 class="text-white-50 text-uppercase small mb-2">About</h6>
                    <p class="text-white">${attr.description}</p>
                </div>`;
        }

        // Notes
        if (activity.notes && activity.notes !== attr.description) {
            content += `
                <div class="mb-3">
                    <h6 class="text-white-50 text-uppercase small mb-2">Travel Notes</h6>
                    <p class="text-info"><i class="fas fa-info-circle me-2"></i>${activity.notes}</p>
                </div>`;
        }

        // Action buttons
        content += `<div class="d-flex gap-2 mt-4">`;

        if (attr.coordinates) {
            const dirLink = `https://www.google.com/maps/dir/?api=1&destination=${attr.coordinates.latitude},${attr.coordinates.longitude}`;
            content += `
                <a href="${dirLink}" target="_blank" class="btn btn-primary flex-fill">
                    <i class="fas fa-location-arrow me-2"></i>Get Directions
                </a>`;
        }

        if (attr.wikipedia_url) {
            content += `
                <a href="${attr.wikipedia_url}" target="_blank" class="btn btn-outline-light flex-fill">
                    <i class="fab fa-wikipedia-w me-2"></i>Read More
                </a>`;
        }

        content += `</div></div>`;

        bodyEl.innerHTML = content;

        // Show modal
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    };

    // Trip Planner Logic
    const plannerForm = document.getElementById('trip-planner-form');
    const plannerResults = document.getElementById('itinerary-results');

    if (plannerForm) {
        plannerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const destinationInput = document.getElementById('plan-destination').value;
            const origin = document.getElementById('plan-origin').value;
            const days = document.getElementById('plan-days').value;

            plannerResults.innerHTML = '<div class="text-center w-100"><div class="spinner-border text-success" role="status"></div><p class="mt-2">Generating your dream itinerary...</p></div>';

            try {
                // Construct query parameters
                const params = new URLSearchParams({
                    destination: destinationInput,
                    days: days
                });
                if (origin) params.append('origin', origin);

                const response = await fetch(`/api/plan?${params.toString()}`);
                const data = await response.json();

                plannerResults.innerHTML = '';

                if (data.error) {
                    plannerResults.innerHTML = `<div class="alert alert-danger w-100">${data.error}</div>`;
                    return;
                }

                // Render Itinerary (Adapt based on actual API response structure)
                // Assuming data.itinerary is a list of days or similar

                const container = document.createElement('div');
                container.className = 'glass-card p-4';

                // Budget and Recommendations
                let html = '';
                if (data.estimated_budget) {
                    const b = data.estimated_budget;
                    html += `
                        <div class="row mb-4">
                            <div class="col-md-12">
                                <div class="card bg-dark text-white border-secondary">
                                    <div class="card-body">
                                        <h5 class="card-title text-warning"><i class="fas fa-coins me-2"></i>Estimated Budget</h5>
                                        <div class="row text-center mt-3">
                                            <div class="col">
                                                <small class="text-white-50">Accommodation</small><br>
                                                <span class="fw-bold">${b.currency} ${b.accommodation}</span>
                                            </div>
                                            <div class="col">
                                                <small class="text-white-50">Food</small><br>
                                                <span class="fw-bold">${b.currency} ${b.food}</span>
                                            </div>
                                            <div class="col">
                                                <small class="text-white-50">Activities</small><br>
                                                <span class="fw-bold">${b.currency} ${b.activities}</span>
                                            </div>
                                            <div class="col">
                                                <small class="text-white-50">Total</small><br>
                                                <span class="h5 text-success fw-bold">${b.currency} ${b.total}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                }

                if (data.recommendations && data.recommendations.length > 0) {
                    html += `
                        <div class="alert alert-info mb-4">
                            <strong><i class="fas fa-lightbulb me-2"></i>Top Tips:</strong>
                            <ul class="mb-0 mt-2">
                                ${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }

                if (data.itinerary) {
                    // Store current plan for saving
                    window.currentPlan = {
                        destination: destinationInput,
                        start_date: null,
                        end_date: null,
                        itinerary: data.itinerary
                    };



                    let actionButtons = `
                        <div class="text-center mt-4 mb-4 d-flex justify-content-center gap-3">
                    `;

                    // Add Save Button if logged in
                    if (localStorage.getItem('token')) {
                        actionButtons += `
                            <button class="btn btn-primary btn-lg btn-glow" onclick="saveCurrentTrip()"><i class="fas fa-save me-2"></i>Save This Trip</button>
                        `;
                    }
                    actionButtons += `</div>`;
                    html += actionButtons;


                    data.itinerary.forEach((dayPlan, index) => {
                        html += `
                            <div class="itinerary-day mb-5">
                                <h4 class="text-secondary border-bottom border-secondary pb-2 mb-3">Day ${index + 1} <span class="text-muted fs-6 ms-2">${dayPlan.summary || ''}</span></h4>
                                <div class="timeline">
                                    ${(dayPlan.activities || []).map((act, actIndex) => {
                            const attr = act.attraction;
                            const hasImage = attr && attr.image;

                            // Create a safe ID for this activity
                            const actId = `act_${index}_${actIndex}`;

                            // Store activity data for modal access
                            if (!window.activityData) window.activityData = {};
                            window.activityData[actId] = act;

                            return `
                                        <div class="card mb-3 border-0 bg-transparent activity-card" 
                                             style="cursor: pointer; transition: all 0.3s ease;"
                                             onmouseover="this.style.transform='translateX(8px)'; this.style.backgroundColor='rgba(255,255,255,0.05)';"
                                             onmouseout="this.style.transform='translateX(0)'; this.style.backgroundColor='transparent';"
                                             onclick="showActivityDetails(window.activityData['${actId}'])">
                                            <div class="row g-0">
                                                <div class="col-md-2 text-center pt-2">
                                                    <span class="badge bg-primary rounded-pill px-3 py-2">${act.time}</span>
                                                </div>
                                                <div class="col-md-${hasImage ? '8' : '10'}">
                                                    <div class="card-body py-2">
                                                        <h5 class="card-title fw-bold text-white mb-1">
                                                            ${attr ? attr.name : 'Activity'}
                                                            <i class="fas fa-chevron-right ms-2 small text-white-50"></i>
                                                        </h5>
                                                        <p class="card-text text-white-50 small mb-2">${attr && attr.description ? (attr.description.length > 100 ? attr.description.substring(0, 100) + '...' : attr.description) : (act.notes || '')}</p>
                                                        <small class="text-info"><i class="fas fa-info-circle me-1"></i>Click for details</small>
                                                    </div>
                                                </div>
                                                ${hasImage ? `
                                                <div class="col-md-2">
                                                    <img src="${attr.image}" class="img-fluid rounded-3 h-100 object-fit-cover" alt="${attr.name}" onerror="this.style.display='none'">
                                                </div>
                                                ` : ''}
                                            </div>
                                        </div>
                                        `;
                        }).join('')}
                                </div>
                            </div>
                        `;
                    });
                } else {
                    // Fallback if structure is different
                    html += `<pre class="text-white bg-dark p-3 rounded">${JSON.stringify(data, null, 2)}</pre>`;
                }

                container.innerHTML = html;
                plannerResults.appendChild(container);

            } catch (error) {
                console.error('Error:', error);
                plannerResults.innerHTML = `<div class="alert alert-danger w-100">An error occurred while generating the plan.</div>`;
            }
        });
    }

    // Save Trip Helper
    window.saveCurrentTrip = async () => {
        if (!window.currentPlan) return;

        try {
            const response = await fetch('/api/trips', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(window.currentPlan)
            });

            if (response.ok) {
                if (typeof showToast === 'function') showToast('Trip saved successfully!', 'success');
                else alert('Trip saved successfully!');
            } else {
                throw new Error('Failed to save trip');
            }
        } catch (e) {
            if (typeof showToast === 'function') showToast(e.message, 'error');
            else alert(e.message);
        }
    };

    // Load Saved Trips Logic
    window.loadSavedTrips = async () => {
        const modal = new bootstrap.Modal(document.getElementById('savedTripsModal'));
        modal.show();

        const listContainer = document.getElementById('saved-trips-list');
        listContainer.innerHTML = '<div class="text-center text-white-50">Loading...</div>';

        try {
            const response = await fetch('/api/trips', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            const trips = await response.json();

            if (trips.length === 0) {
                listContainer.innerHTML = '<div class="alert alert-info w-100">No saved trips found. Start planning!</div>';
                return;
            }

            listContainer.innerHTML = trips.map(trip => `
                <div class="col-md-6">
                    <div class="glass-card p-3 h-100">
                        <h5 class="fw-bold text-white">${trip.destination}</h5>
                        <small class="text-white-50">Created: ${new Date(trip.created_at).toLocaleDateString()}</small>
                        <button class="btn btn-sm btn-outline-primary mt-2 d-block w-100" onclick="alert('Viewing functionality coming soon!')">View Itinerary</button>
                    </div>
                </div>
            `).join('');

        } catch (e) {
            listContainer.innerHTML = '<div class="text-danger">Failed to load trips.</div>';
        }
    };

    // --- Dashboard Logic ---
    const dashboardContainer = document.getElementById('dashboard-container');
    if (dashboardContainer) {
        // Redirect if not logged in
        if (!localStorage.getItem('token')) {
            window.location.href = '/';
        } else {
            loadDashboardData();
        }
    }

    async function loadDashboardData() {
        const listContainer = document.getElementById('dashboard-trips-list');
        const countDisplay = document.getElementById('total-trips-count');

        try {
            const response = await fetch('/api/trips', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) throw new Error('Failed to fetch trips: ' + response.statusText);

            const trips = await response.json();

            // Update Stats
            if (countDisplay) countDisplay.textContent = trips.length;

            if (trips.length === 0) {
                listContainer.innerHTML = `
                    <div class="col-12 text-center py-5">
                        <div class="glass-card p-5 d-inline-block">
                            <i class="fas fa-map-signs fa-4x text-white-50 mb-3"></i>
                            <h3 class="text-white">No trips saved yet</h3>
                            <p class="text-white-50">Start planning your first adventure!</p>
                            <a href="/#planner" class="btn btn-primary btn-glow mt-3">Create New Trip</a>
                        </div>
                    </div>
                `;
                return;
            }

            listContainer.innerHTML = trips.map(trip => {
                // Parse itinerary to get preview image and stats
                let itineraryData;
                let previewImage = null;
                let dayCount = 0;
                let activityCount = 0;

                try {
                    itineraryData = typeof trip.itinerary === 'string' ? JSON.parse(trip.itinerary) : trip.itinerary;
                    if (Array.isArray(itineraryData)) {
                        dayCount = itineraryData.length;
                        // Find first image from activities
                        for (const day of itineraryData) {
                            activityCount += (day.activities || []).length;
                            if (!previewImage) {
                                for (const act of (day.activities || [])) {
                                    if (act.attraction?.image) {
                                        previewImage = act.attraction.image;
                                        break;
                                    }
                                }
                            }
                        }
                    }
                } catch (e) {
                    console.error('Error parsing itinerary:', e);
                }

                return `
                <div class="col-md-6 col-lg-4">
                    <div class="glass-card h-100 p-0 overflow-hidden trip-card-hover" style="transition: all 0.3s ease;">
                        ${previewImage ? `
                        <div class="position-relative" style="height: 200px; overflow: hidden;">
                            <img src="${previewImage}" class="w-100 h-100 object-fit-cover" alt="${trip.destination}" 
                                 style="transition: transform 0.3s ease;"
                                 onmouseover="this.style.transform='scale(1.1)'"
                                 onmouseout="this.style.transform='scale(1)'">
                            <div class="position-absolute top-0 start-0 end-0 bottom-0" 
                                 style="background: linear-gradient(to bottom, rgba(0,0,0,0.3), rgba(0,0,0,0.7));"></div>
                            <div class="position-absolute bottom-0 start-0 p-3">
                                <h4 class="fw-bold text-white mb-0">${trip.destination}</h4>
                                <small class="text-white-50"><i class="fas fa-calendar-alt me-1"></i> ${new Date(trip.created_at).toLocaleDateString()}</small>
                            </div>
                        </div>
                        ` : `
                        <div class="trip-card-header p-4 bg-gradient-primary">
                            <h4 class="fw-bold text-white mb-1">${trip.destination}</h4>
                            <small class="text-white-50"><i class="fas fa-calendar-alt me-1"></i> ${new Date(trip.created_at).toLocaleDateString()}</small>
                        </div>
                        `}
                        <div class="p-4">
                            <div class="d-flex justify-content-between mb-3">
                                <div class="text-center flex-fill">
                                    <div class="text-primary fw-bold h5 mb-0">${dayCount}</div>
                                    <small class="text-white-50">Days</small>
                                </div>
                                <div class="text-center flex-fill border-start border-end border-secondary">
                                    <div class="text-success fw-bold h5 mb-0">${activityCount}</div>
                                    <small class="text-white-50">Activities</small>
                                </div>
                                <div class="text-center flex-fill">
                                    <div class="text-warning fw-bold h5 mb-0"><i class="fas fa-star"></i></div>
                                    <small class="text-white-50">Saved</small>
                                </div>
                            </div>
                            <div class="d-grid gap-2">
                                <button class="btn btn-primary btn-glow" onclick="viewTrip(${trip.id})">
                                    <i class="fas fa-eye me-2"></i> View Itinerary
                                </button>
                                <button class="btn btn-sm btn-outline-danger border-0" onclick="deleteTrip(${trip.id})">
                                    <i class="fas fa-trash me-2"></i> Delete Trip
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            }).join('');

        } catch (e) {
            console.error(e);
            listContainer.innerHTML = '<div class="alert alert-danger">Failed to load trips.</div>';
        }
    }

    // View Trip Details
    window.viewTrip = async (tripId) => {
        const modal = new bootstrap.Modal(document.getElementById('viewTripModal'));
        const modalBody = document.getElementById('viewTripBody');
        modalBody.innerHTML = '<div class="text-center p-5"><span class="spinner-border text-primary"></span></div>';
        modal.show();

        try {
            // In a real app, we might want a specific endpoint for single trip, 
            // but we can also filter from the list if we already have it, or fetch again.
            // For now, let's fetch all (since we don't have a single GET endpoint exposed/documented yet in app.js context, 
            // though the backend might support it, let's just re-fetch list for simplicity or improve backend later).
            // actually, let's assume we can pass the data if we had it, but separate fetch is cleaner.
            // Wait, the backend has `get_trips`, but maybe not `get_trip/{id}`? 
            // Checking schemas... `crud.py` has `get_trips` and `create_trip`. It does NOT seem to have get_trip_by_id exposed in router.
            // We will fetch all and find it for now.

            const response = await fetch('/api/trips', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            const trips = await response.json();
            const trip = trips.find(t => t.id === tripId);

            if (!trip) throw new Error('Trip not found');

            // Render Itinerary (Reusing logic logic or simplifying)
            let itineraryData;
            try {
                // Itinerary might be string or object depending on how it was saved/returned
                itineraryData = typeof trip.itinerary === 'string' ? JSON.parse(trip.itinerary) : trip.itinerary;
            } catch (e) {
                itineraryData = [];
            }

            // We need to be able to pass this trip's itinerary to initMap.
            // Since this is async and we have the data right here, we can store it in a temporary global or passed argument.
            window.tempTripItinerary = itineraryData;

            let html = `
                <div class="text-center mb-4">
                    <h3 class="text-white mb-3">Trip to ${trip.destination}</h3>
                </div>
            `;

            if (Array.isArray(itineraryData)) {
                itineraryData.forEach((dayPlan, index) => {
                    html += `
                        <div class="itinerary-day mb-5">
                            <h4 class="text-secondary border-bottom border-secondary pb-2 mb-3">Day ${index + 1} <span class="text-muted fs-6 ms-2">${dayPlan.summary || ''}</span></h4>
                            <div class="timeline">
                                ${(dayPlan.activities || []).map((act, actIndex) => {
                        const attr = act.attraction;
                        const hasImage = attr && attr.image;

                        // Create a safe ID for this activity
                        const actId = `saved_act_${tripId}_${index}_${actIndex}`;

                        // Store activity data for modal access
                        if (!window.activityData) window.activityData = {};
                        window.activityData[actId] = act;

                        return `
                                    <div class="card mb-3 border-0 bg-transparent activity-card" 
                                         style="cursor: pointer; transition: all 0.3s ease;"
                                         onmouseover="this.style.transform='translateX(8px)'; this.style.backgroundColor='rgba(255,255,255,0.05)';"
                                         onmouseout="this.style.transform='translateX(0)'; this.style.backgroundColor='transparent';"
                                         onclick="showActivityDetails(window.activityData['${actId}'])">
                                        <div class="row g-0">
                                            <div class="col-md-2 text-center pt-2">
                                                <span class="badge bg-primary rounded-pill px-3 py-2">${act.time || ''}</span>
                                            </div>
                                            <div class="col-md-${hasImage ? '8' : '10'}">
                                                <div class="card-body py-2">
                                                    <h5 class="card-title fw-bold text-white mb-1">
                                                        ${attr ? attr.name : (act.description || 'Activity')}
                                                        <i class="fas fa-chevron-right ms-2 small text-white-50"></i>
                                                    </h5>
                                                    <p class="card-text text-white-50 small mb-2">${attr && attr.description ? (attr.description.length > 100 ? attr.description.substring(0, 100) + '...' : attr.description) : (act.notes || '')}</p>
                                                    <small class="text-info"><i class="fas fa-info-circle me-1"></i>Click for details</small>
                                                </div>
                                            </div>
                                            ${hasImage ? `
                                            <div class="col-md-2">
                                                <img src="${attr.image}" class="img-fluid rounded-3 h-100 object-fit-cover" alt="${attr.name}" onerror="this.style.display='none'">
                                            </div>
                                            ` : ''}
                                        </div>
                                    </div>
                                    `;
                    }).join('')}
                            </div>
                        </div>
                    `;
                });
            } else {
                html += `<div class="alert alert-warning">Itinerary data format not recognized.</div>`;
            }

            modalBody.innerHTML = html;

        } catch (e) {
            modalBody.innerHTML = `<div class="alert alert-danger">${e.message}</div>`;
        }
    };

    // Delete Trip Handler
    let tripToDeleteId = null;

    window.deleteTrip = (tripId) => {
        tripToDeleteId = tripId;
        const modal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
        modal.show();
    };

    // Attach listener to confirming delete
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', async () => {
            console.log('Delete button clicked! Trip ID:', tripToDeleteId);
            const btn = confirmDeleteBtn;
            const originalText = btn.innerHTML;

            if (!tripToDeleteId) return;

            try {
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Deleting...';

                const response = await fetch(`/api/trips/${tripToDeleteId}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });

                if (response.ok) {
                    showToast('Trip deleted successfully.', 'success');
                    // Refresh Dashboard
                    loadDashboardData();
                } else {
                    throw new Error('Failed to delete trip');
                }

            } catch (error) {
                showToast('Error deleting trip: ' + error.message, 'error');
            } finally {
                // Close Modal and Reset
                const modalEl = document.getElementById('deleteConfirmModal');
                const modal = bootstrap.Modal.getInstance(modalEl);
                modal.hide();

                btn.disabled = false;
                btn.innerHTML = originalText;
                tripToDeleteId = null;
            }
        });
    }

});
