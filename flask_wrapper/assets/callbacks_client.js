window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        // Update frame of video
        positionUpdate: function(nclicks, nclicks2, nclicks3, nclicks4, nclicks5, nclicks6, nclicks7, nclicks8,currentTime, duration) {

            // slider area
            const green_bar_pelvis_rot = document.getElementById('green_bar_pelvis_rot');
            const green_bar_pelvis_bend = document.getElementById('green_bar_pelvis_bend');
            const green_bar_thorax_rot = document.getElementById('green_bar_thorax_rot');
            const green_bar_thorax_bend = document.getElementById('green_bar_thorax_bend');
            const green_bar_head_rot = document.getElementById('green_bar_head_rot');
            const green_bar_head_tilt = document.getElementById('green_bar_head_tilt');

            // console.log(window.dash_clientside.callback_context.triggered[0].prop_id)
            if (window.dash_clientside.callback_context.triggered[0].prop_id === 'top_pos_button.n_clicks') {

                // console.log(nclicks)
                const top_pos = document.getElementById('top_pos');
                const top_index = top_pos.innerText;
                if (nclicks > 0) {
                    green_bar_pelvis_rot.style.left = (80 -55.9) / (240) * 100 + '%';
                    green_bar_pelvis_rot.style.right = (160 + 39.9) / (240) * 100 + '%';

                    green_bar_pelvis_bend.style.left = (30 - 14.1) / (60) * 100 + '%';
                    green_bar_pelvis_bend.style.right = (30 + 6.3) / (60) * 100 + '%';

                    green_bar_thorax_rot.style.left = (140 - 98) / (280) * 100 + '%';
                    green_bar_thorax_rot.style.right = (140 + 84) / (280) * 100 + '%';

                    green_bar_thorax_bend.style.left = (20 - 5) / (80) * 100 + '%';
                    green_bar_thorax_bend.style.right = (60 - 8) / (80) * 100 + '%';

                    green_bar_head_rot.style.left = (100 - 25) / (200) * 100 + '%';
                    green_bar_head_rot.style.right = (100 + 9) / (200) * 100 + '%';

                    green_bar_head_tilt.style.left = (60 - 16) / (120) * 100 + '%';
                    green_bar_head_tilt.style.right = (60 - 4) / (120) * 100 + '%';

                    return top_index;
                }
            }

            else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'impact_pos_button.n_clicks') {
                // console.log(nclicks2)
                    const impact_pos = document.getElementById('impact_pos');
                    const impact_index = impact_pos.innerText;
                    if (nclicks2 > 0) {
                        green_bar_pelvis_rot.style.left = (80 + 29.5) / (240) * 100 + '%';
                        green_bar_pelvis_rot.style.right = (160 - 48.3) / (240) * 100 + '%';

                        green_bar_pelvis_bend.style.left = (30 - 1.5) / (60) * 100 + '%';
                        green_bar_pelvis_bend.style.right = (30 - 11.1) / (60) * 100 + '%';

                        green_bar_thorax_rot.style.left = (140 + 20.5) / (280) * 100 + '%';
                        green_bar_thorax_rot.style.right = (140 - 36.7) / (280) * 100 + '%';

                        green_bar_thorax_bend.style.left = (20 + 26.7) / (80) * 100 + '%';
                        green_bar_thorax_bend.style.right = (60 - 36.7) / (80) * 100 + '%';

                        green_bar_head_rot.style.left = (100 - 6) / (200) * 100 + '%';
                        green_bar_head_rot.style.right = (100 - 15) / (200) * 100 + '%';

                        green_bar_head_tilt.style.left = (60 + 1) / (120) * 100 + '%';
                        green_bar_head_tilt.style.right = (60 - 18) / (120) * 100 + '%';

                        return impact_index;
                }
            }

            else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'end_pos_button.n_clicks') {
                const end_pos = document.getElementById('end_pos');
                const end_index = end_pos.innerText;
                if (nclicks3 > 0) {
                    green_bar_pelvis_rot.style.left = '0%';
                    green_bar_pelvis_rot.style.right = '0%';

                    green_bar_pelvis_bend.style.left = '0%';
                    green_bar_pelvis_bend.style.right = '0%';

                    green_bar_thorax_rot.style.left = '0%';
                    green_bar_thorax_rot.style.right = '0%';

                    green_bar_thorax_bend.style.left = '0%';
                    green_bar_thorax_bend.style.right = '0%';

                    green_bar_head_rot.style.left = '0%';
                    green_bar_head_rot.style.right = '0%';

                    green_bar_head_tilt.style.left = '0%';
                    green_bar_head_tilt.style.right = '0%';

                    return end_index;
                }
            }

            else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'setup_pos_button.n_clicks') {
                const setup_pos = document.getElementById('setup_pos');
                const setup_index = setup_pos.innerText;
                if (nclicks4 > 0) {
                    green_bar_pelvis_rot.style.left = (80 - 2.8) / (240) * 100 + '%';
                    green_bar_pelvis_rot.style.right = (160 - 6) / (240) * 100 + '%';

                    green_bar_pelvis_bend.style.left = (30 - 3.4) / (60) * 100 + '%';
                    green_bar_pelvis_bend.style.right = (30 - 3.2) / (60) * 100 + '%';

                    green_bar_thorax_rot.style.left = (140 + 7) / (280) * 100 + '%';
                    green_bar_thorax_rot.style.right = (140 - 15) / (280) * 100 + '%';

                    green_bar_thorax_bend.style.left = (20 + 11) / (80) * 100 + '%';
                    green_bar_thorax_bend.style.right = (60 - 18) / (80) * 100 + '%';

                    green_bar_head_rot.style.left = (100 - 6) / (200) * 100 + '%';
                    green_bar_head_rot.style.right = (100 - 6) / (200) * 100 + '%';

                    green_bar_head_tilt.style.left = (60 - 3) / (120) * 100 + '%';
                    green_bar_head_tilt.style.right = (60 - 7) / (120) * 100 + '%';

                    return setup_index;
                }
            }

            else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'minus_frame.n_clicks') {
                const fps_saved = document.getElementById('fps_saved');
                const fps = fps_saved.innerText;
                if (nclicks5 > 0) {
                    const time = (currentTime - 1/fps)/duration
                    if (time < 0) {
                        return 0;
                    }
                    return time;
                }
            }

            else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'plus_frame.n_clicks') {
                const fps_saved = document.getElementById('fps_saved');
                const fps = fps_saved.innerText;
                if (nclicks6 > 0) {
                    const time = (currentTime + 1/fps)/duration
                    if (time > 1) {
                        return 0.999;
                    }
                    return time;
                }
            }

            else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'minus_frame_mobile.n_clicks') {
                const fps_saved = document.getElementById('fps_saved');
                const fps = fps_saved.innerText;
                if (nclicks7 > 0) {
                    const time = (currentTime - 1/fps)/duration
                    if (time < 0) {
                        return 0;
                    }
                    return time;
                }
            }

            else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'plus_frame_mobile.n_clicks') {
                const fps_saved = document.getElementById('fps_saved');
                const fps = fps_saved.innerText;
                if (nclicks8 > 0) {
                    const time = (currentTime + 1/fps)/duration
                    if (time > 1) {
                        return 0.999;
                    }
                    return time;
                }
            }

            else {
                return currentTime;
            }

        },

        // Update the vertical line on the sequence plot
        drawVerticalLine: function(currentTime, fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10) {

            // console.log(sequence.layout.shapes[0].x0)
            // console.log(fig1)

            function drawLine (fig, time, id) {
                fig.layout.shapes[0].x0 = time;
                fig.layout.shapes[0].x1 = time;
                Plotly.react(id , fig.data, fig.layout, {displayModeBar: false});
            }

            drawLine(fig1, currentTime, 'sequence');
            drawLine(fig2, currentTime, 'pelvis_rotation');
            drawLine(fig3, currentTime, 'pelvis_displacement');
            drawLine(fig4, currentTime, 'thorax_rotation');
            drawLine(fig5, currentTime, 'thorax_displacement');
            drawLine(fig6, currentTime, 's_tilt');
            drawLine(fig7, currentTime, 'h_tilt');
            drawLine(fig8, currentTime, 'h_rotation');
            drawLine(fig9, currentTime, 'arm_length');
            drawLine(fig10, currentTime, 'spine_rotation');

        },

        updateValues: function(currentTime, duration, fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10, fig11, impact_button_time, top_button_time, end_button_time, setup_button_time) {
            const pelvis_rotation = fig2.data[1].y;
            const pelvis_bend = fig2.data[0].y;
            const thorax_rotation = fig4.data[0].y;
            const thorax_bend = fig4.data[1].y;
            const head_tilt = fig7.data[0].y;
            const head_rotation = fig8.data[0].y;
            const arm_rotation = fig11.data[0].y;
            const arm_ground = fig11.data[1].y;

            const index = Math.floor(pelvis_rotation.length * (currentTime / duration))

            const value_pelvis_rotation = Math.round(pelvis_rotation[index]);
            const value_pelvis_bend = Math.round(pelvis_bend[index]);
            const value_thorax_rotation = Math.round(thorax_rotation[index]);
            const value_thorax_bend = Math.round(thorax_bend[index]);
            const value_head_tilt = Math.round(head_tilt[index]);
            const value_head_rotation = Math.round(head_rotation[index]);
            const value_arm_rotation = Math.round(arm_rotation[index]);
            const value_arm_ground = Math.round(arm_ground[index]);

            // Color the values
            const pelvis_rot_div = document.getElementById('pelvis_rot_val');
            const pelvis_bend_div = document.getElementById('pelvis_bend_val');
            const thorax_rot_div = document.getElementById('thorax_rot_val');
            const thorax_bend_div = document.getElementById('thorax_bend_val');
            const head_rot_div = document.getElementById('head_rot_val');
            const head_tilt_div = document.getElementById('head_tilt_val');
            const arm_rot_div = document.getElementById('arm_rot_val');
            const arm_ground_div = document.getElementById('arm_ground_val');

            // Sliders
            const slider_pelvis_rot = document.getElementById('slider_pelvis_rot');
            const slider_pelvis_bend = document.getElementById('slider_pelvis_bend');
            const slider_thorax_rot = document.getElementById('slider_thorax_rot');
            const slider_thorax_bend = document.getElementById('slider_thorax_bend');
            const slider_head_rot = document.getElementById('slider_head_rot');
            const slider_head_tilt = document.getElementById('slider_head_tilt');
            const slider_arm_rot = document.getElementById('slider_arm_rot');
            const slider_arm_ground = document.getElementById('slider_arm_ground');

            if (impact_button_time === undefined) {
                impact_button_time = -1
            }
            if (top_button_time === undefined) {
                top_button_time = -1
            }
            if (end_button_time === undefined) {
                end_button_time = -1
            }
            if (setup_button_time === undefined) {
                setup_button_time = -1
            }

            const button_recent = {'impact': impact_button_time, 'top': top_button_time, 'end': end_button_time, 'setup': setup_button_time, 'default': 0}
            // sort button_recent by value
            const button_recent_sorted = Object.keys(button_recent).sort(function(a,b){return button_recent[a]-button_recent[b]})
            // get the most recent button
            const button_recent_name = button_recent_sorted[button_recent_sorted.length - 1]

            if (button_recent_name === 'impact') {
                pelvis_rot_div.style.color = ((value_pelvis_rotation < 29.5) || (value_pelvis_rotation > 48.3)) ? 'red' : 'green';
                pelvis_bend_div.style.color = ((value_pelvis_bend < -1.5) || (value_pelvis_bend > 11.1)) ? 'red' : 'green';
                thorax_rot_div.style.color = ((value_thorax_rotation < 20.5) || (value_thorax_rotation > 36.7)) ? 'red' : 'green';
                thorax_bend_div.style.color = ((value_thorax_bend < 26.7) || (value_thorax_bend > 36.7)) ? 'red' : 'green';
                head_rot_div.style.color = ((value_head_rotation < -6.1) || (value_head_rotation > 14.7)) ? 'red' : 'green';
                head_tilt_div.style.color = ((value_head_tilt < 1.7) || (value_head_tilt > 18.3)) ? 'red' : 'green';
                // arm_rot_div.style.color = ((value_arm_rotation < 0.5) || (value_arm_rotation > 3.5)) ? 'red' : 'green';
                // arm_ground_div.style.color = ((value_arm_ground < 0.5) || (value_arm_ground > 3.5)) ? 'red' : 'green';

            }
            else if (button_recent_name === 'top') {
                pelvis_rot_div.style.color = ((value_pelvis_rotation < -55.9) || (value_pelvis_rotation > -39.9)) ? 'red' : 'green';
                pelvis_bend_div.style.color = ((value_pelvis_bend < -14.1) || (value_pelvis_bend > -6.3)) ? 'red' : 'green';
                thorax_rot_div.style.color = ((value_thorax_rotation < -97.8) || (value_thorax_rotation > -83.4)) ? 'red' : 'green';
                thorax_bend_div.style.color = ((value_thorax_bend < -4.8) || (value_thorax_bend > 7.8)) ? 'red' : 'green';
                head_rot_div.style.color = ((value_head_rotation < -24.8) || (value_head_rotation > -8.8)) ? 'red' : 'green';
                head_tilt_div.style.color = ((value_head_tilt < -16.3) || (value_head_tilt > -3.7)) ? 'red' : 'green';
            }
            else if (button_recent_name === 'setup') {
                pelvis_rot_div.style.color = ((value_pelvis_rotation < -2.8) || (value_pelvis_rotation > 6)) ? 'red' : 'green';
                pelvis_bend_div.style.color = ((value_pelvis_bend < -3.4) || (value_pelvis_bend > 3.2)) ? 'red' : 'green';
                thorax_rot_div.style.color = ((value_thorax_rotation < 7) || (value_thorax_rotation > 14.6)) ? 'red' : 'green';
                thorax_bend_div.style.color = ((value_thorax_bend < 11) || (value_thorax_bend > 17.4)) ? 'red' : 'green';
                head_rot_div.style.color = ((value_head_rotation < -5.8) || (value_head_rotation > 5.6)) ? 'red' : 'green';
                head_tilt_div.style.color = ((value_head_tilt < -3.2) || (value_head_tilt > 7.2)) ? 'red' : 'green';
            }
            else {
                pelvis_rot_div.style.color = '';
                pelvis_bend_div.style.color = '';
                thorax_rot_div.style.color = '';
                thorax_bend_div.style.color = '';
                head_rot_div.style.color = '';
                head_tilt_div.style.color = '';
            }

            if (isNaN(value_pelvis_rotation)) {
                return ['-°', '-°', '-°', '-°', '-°', '-°', '-°', '-°'];
            }

            // Move sliders
            slider_pelvis_rot.style.left = (value_pelvis_rotation + 80) / (240) * 100 + '%';
            slider_pelvis_bend.style.left = (value_pelvis_bend + 40) / (80) * 100 + '%';
            slider_thorax_rot.style.left = (value_thorax_rotation + 140) / (280) * 100 + '%';
            slider_thorax_bend.style.left = (value_thorax_bend + 20) / (80) * 100 + '%';
            slider_head_rot.style.left = (value_head_rotation + 100) / (200) * 100 + '%';
            slider_head_tilt.style.left = (value_head_tilt + 60) / (120) * 100 + '%';
            slider_arm_rot.style.left = (value_arm_rotation + 240) / (480) * 100 + '%';
            slider_arm_ground.style.left = (value_arm_ground + 90) / (180) * 100 + '%';

            return [`${value_pelvis_rotation}°`, `${value_pelvis_bend}°`, `${value_thorax_rotation}°`, `${value_thorax_bend}°`,
                `${value_head_rotation}°`, `${value_head_tilt}°`, `${value_arm_rotation}°`, `${value_arm_ground}°`];
        },

        showNavbar: function(n_clicks, header_clicks, sidebar_class) {
            if (window.dash_clientside.callback_context.triggered[0].prop_id === 'menu-button.n_clicks') {
                sidebar_class = sidebar_class.replace('hidden', 'flex')

                return sidebar_class
            }

            sidebar_class = sidebar_class.replace('flex', 'hidden')

            return sidebar_class

        },

        hideSelectionView: function(n_clicks, selection_class) {
            if (n_clicks > 0) {
                return selection_class.replace('flex', 'hidden');
            }
        },

        showSelectionView: function(n_clicks, n_clicks2, n_clicks3, n_clicks4, n_clicks5, n_clicks6, selection_class) {

                const title = document.getElementById('new_margins_title');

                if (window.dash_clientside.callback_context.triggered[0].prop_id === 'pelvis_rot_btn.n_clicks') {
                    title.innerHTML = 'New Margins for Pelvis Rot.';
                }

                else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'pelvis_tilt_btn.n_clicks') {
                    title.innerHTML = 'New Margins for Pelvis Tilt';
                }

                else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'thorax_rot_btn.n_clicks') {
                    title.innerHTML = 'New Margins for Thorax Rot.';
                }

                else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'thorax_tilt_btn.n_clicks') {
                    title.innerHTML = 'New Margins for Thorax Tilt';
                }

                else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'head_rot_btn.n_clicks') {
                    title.innerHTML = 'New Margins for Head Rot.';
                }

                else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'head_tilt_btn.n_clicks') {
                    title.innerHTML = 'New Margins for Head Tilt';
                }

                else {
                    title.innerHTML = 'New Margins';
                }

                return selection_class.replace('hidden', 'flex');

        }

    }
});
