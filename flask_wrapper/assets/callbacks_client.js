window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        // Update frame of video
        positionUpdate: function(nclicks, nclicks2, nclicks3, nclicks4, nclicks5, nclicks6, nclicks7, nclicks8,currentTime, duration) {

            // console.log('positionUpdate')

            // slider area
            const green_bar_pelvis_rot = document.getElementById('green_bar_pelvis_rot');
            const green_bar_pelvis_bend = document.getElementById('green_bar_pelvis_bend');
            const green_bar_thorax_rot = document.getElementById('green_bar_thorax_rot');
            const green_bar_thorax_bend = document.getElementById('green_bar_thorax_bend');
            const green_bar_head_rot = document.getElementById('green_bar_head_rot');
            const green_bar_head_tilt = document.getElementById('green_bar_head_tilt');

            // buttons
            let setup_pos_button = document.getElementById('setup_pos_button');
            let top_pos_button = document.getElementById('top_pos_button');
            let impact_pos_button = document.getElementById('impact_pos_button');
            let end_pos_button = document.getElementById('end_pos_button');

            // Settings
            let edit_positions = document.getElementById('edit_positions').classList;

            // console.log(window.dash_clientside.callback_context.triggered[0].prop_id)
            if (window.dash_clientside.callback_context.triggered[0].prop_id === 'top_pos_button.n_clicks') {
                top_pos_button.classList.replace('bg-indigo-500', 'bg-indigo-700');
                setup_pos_button.classList.replace('bg-indigo-700', 'bg-indigo-500');
                impact_pos_button.classList.replace('bg-indigo-700', 'bg-indigo-500');
                end_pos_button.classList.replace('bg-indigo-700', 'bg-indigo-500');

                // console.log(nclicks)
                const top_pos = document.getElementById('top_pos');
                const top_index = top_pos.innerText;

                const pelvis_rot_margins = document.getElementById('pelvis_rot_store').innerHTML.split(', ');
                const pelvis_bend_margins = document.getElementById('pelvis_bend_store').innerHTML.split(', ');
                const thorax_rot_margins = document.getElementById('thorax_rot_store').innerHTML.split(', ');
                const thorax_bend_margins = document.getElementById('thorax_bend_store').innerHTML.split(', ');
                const head_rot_margins = document.getElementById('head_rot_store').innerHTML.split(', ');
                const head_tilt_margins = document.getElementById('head_tilt_store').innerHTML.split(', ');

                edit_positions.remove('hidden');

                if (nclicks > 0) {
                    green_bar_pelvis_rot.style.left = (80 + Number(pelvis_rot_margins[2])) / (240) * 100 + '%';
                    green_bar_pelvis_rot.style.right = (160 - Number(pelvis_rot_margins[3])) / (240) * 100 + '%';

                    green_bar_pelvis_bend.style.left = (30 + Number(pelvis_bend_margins[2])) / (60) * 100 + '%';
                    green_bar_pelvis_bend.style.right = (30 - Number(pelvis_bend_margins[3])) / (60) * 100 + '%';

                    green_bar_thorax_rot.style.left = (140 + Number(thorax_rot_margins[2])) / (280) * 100 + '%';
                    green_bar_thorax_rot.style.right = (140 - Number(thorax_rot_margins[3])) / (280) * 100 + '%';

                    green_bar_thorax_bend.style.left = (20 + Number(thorax_bend_margins[2])) / (80) * 100 + '%';
                    green_bar_thorax_bend.style.right = (60 - Number(thorax_bend_margins[3])) / (80) * 100 + '%';

                    green_bar_head_rot.style.left = (100 + Number(head_rot_margins[2])) / (200) * 100 + '%';
                    green_bar_head_rot.style.right = (100 - Number(head_rot_margins[3])) / (200) * 100 + '%';

                    green_bar_head_tilt.style.left = (60 + Number(head_tilt_margins[2])) / (120) * 100 + '%';
                    green_bar_head_tilt.style.right = (60 - Number(head_tilt_margins[3])) / (120) * 100 + '%';

                    return top_index;
                }
            }

            else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'impact_pos_button.n_clicks') {
                    impact_pos_button.classList.replace('bg-indigo-500', 'bg-indigo-700');
                    setup_pos_button.classList.replace('bg-indigo-700', 'bg-indigo-500');
                    top_pos_button.classList.replace('bg-indigo-700', 'bg-indigo-500');
                    end_pos_button.classList.replace('bg-indigo-700', 'bg-indigo-500');

                // console.log(nclicks2)
                    const impact_pos = document.getElementById('impact_pos');
                    const impact_index = impact_pos.innerText;

                    const pelvis_rot_margins = document.getElementById('pelvis_rot_store').innerHTML.split(', ');
                    const pelvis_bend_margins = document.getElementById('pelvis_bend_store').innerHTML.split(', ');
                    const thorax_rot_margins = document.getElementById('thorax_rot_store').innerHTML.split(', ');
                    const thorax_bend_margins = document.getElementById('thorax_bend_store').innerHTML.split(', ');
                    const head_rot_margins = document.getElementById('head_rot_store').innerHTML.split(', ');
                    const head_tilt_margins = document.getElementById('head_tilt_store').innerHTML.split(', ');

                    edit_positions.remove('hidden');

                    if (nclicks2 > 0) {
                        green_bar_pelvis_rot.style.left = (80 + Number(pelvis_rot_margins[4])) / (240) * 100 + '%';
                        green_bar_pelvis_rot.style.right = (160 - Number(pelvis_rot_margins[5])) / (240) * 100 + '%';

                        green_bar_pelvis_bend.style.left = (30 + Number(pelvis_bend_margins[4])) / (60) * 100 + '%';
                        green_bar_pelvis_bend.style.right = (30 - Number(pelvis_bend_margins[5])) / (60) * 100 + '%';

                        green_bar_thorax_rot.style.left = (140 + Number(thorax_rot_margins[4])) / (280) * 100 + '%';
                        green_bar_thorax_rot.style.right = (140 - Number(thorax_rot_margins[5])) / (280) * 100 + '%';

                        green_bar_thorax_bend.style.left = (20 + Number(thorax_bend_margins[4])) / (80) * 100 + '%';
                        green_bar_thorax_bend.style.right = (60 - Number(thorax_bend_margins[5])) / (80) * 100 + '%';

                        green_bar_head_rot.style.left = (100 + Number(head_rot_margins[4])) / (200) * 100 + '%';
                        green_bar_head_rot.style.right = (100 - Number(head_rot_margins[5])) / (200) * 100 + '%';

                        green_bar_head_tilt.style.left = (60 + Number(head_tilt_margins[4])) / (120) * 100 + '%';
                        green_bar_head_tilt.style.right = (60 - Number(head_tilt_margins[5])) / (120) * 100 + '%';

                        return impact_index;
                }
            }

            else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'end_pos_button.n_clicks') {
                end_pos_button.classList.replace('bg-indigo-500', 'bg-indigo-700');
                setup_pos_button.classList.replace('bg-indigo-700', 'bg-indigo-500');
                top_pos_button.classList.replace('bg-indigo-700', 'bg-indigo-500');
                impact_pos_button.classList.replace('bg-indigo-700', 'bg-indigo-500');

                const end_pos = document.getElementById('end_pos');
                const end_index = end_pos.innerText;

                edit_positions.remove('hidden');

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
                setup_pos_button.classList.replace('bg-indigo-500', 'bg-indigo-700');
                top_pos_button.classList.replace('bg-indigo-700', 'bg-indigo-500');
                impact_pos_button.classList.replace('bg-indigo-700', 'bg-indigo-500');
                end_pos_button.classList.replace('bg-indigo-700', 'bg-indigo-500');

                const setup_pos = document.getElementById('setup_pos');
                const setup_index = setup_pos.innerText;

                const pelvis_rot_margins = document.getElementById('pelvis_rot_store').innerHTML.split(', ');
                const pelvis_bend_margins = document.getElementById('pelvis_bend_store').innerHTML.split(', ');
                const thorax_rot_margins = document.getElementById('thorax_rot_store').innerHTML.split(', ');
                const thorax_bend_margins = document.getElementById('thorax_bend_store').innerHTML.split(', ');
                const head_rot_margins = document.getElementById('head_rot_store').innerHTML.split(', ');
                const head_tilt_margins = document.getElementById('head_tilt_store').innerHTML.split(', ');

                edit_positions.remove('hidden');

                // console.log(pelvis_rot_margins)

                if (nclicks4 > 0) {
                    green_bar_pelvis_rot.style.left = (80+ Number(pelvis_rot_margins[0])) / (240) * 100 + '%';
                    green_bar_pelvis_rot.style.right = (160 - Number(pelvis_rot_margins[1])) / (240) * 100 + '%';

                    green_bar_pelvis_bend.style.left = (30 + Number(pelvis_bend_margins[0])) / (60) * 100 + '%';
                    green_bar_pelvis_bend.style.right = (30 - Number(pelvis_bend_margins[1])) / (60) * 100 + '%';

                    green_bar_thorax_rot.style.left = (140 + Number(thorax_rot_margins[0])) / (280) * 100 + '%';
                    green_bar_thorax_rot.style.right = (140 - Number(thorax_rot_margins[1])) / (280) * 100 + '%';

                    green_bar_thorax_bend.style.left = (20 + Number(thorax_bend_margins[0])) / (80) * 100 + '%';
                    green_bar_thorax_bend.style.right = (60 - Number(thorax_bend_margins[1])) / (80) * 100 + '%';

                    green_bar_head_rot.style.left = (100 + Number(head_rot_margins[0])) / (200) * 100 + '%';
                    green_bar_head_rot.style.right = (100 - Number(head_rot_margins[1])) / (200) * 100 + '%';

                    green_bar_head_tilt.style.left = (60 + Number(head_tilt_margins[0])) / (120) * 100 + '%';
                    green_bar_head_tilt.style.right = (60 - Number(head_tilt_margins[1])) / (120) * 100 + '%';

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
            // console.log('updateValues')
            const pelvis_rotation = fig2.data[1].y;
            const pelvis_bend = fig2.data[0].y;
            const thorax_rotation = fig4.data[0].y;
            const thorax_bend = fig4.data[1].y;
            const head_tilt = fig7.data[0].y;
            const head_rotation = fig8.data[0].y;
            const arm_rotation = fig11.data[0].y;
            const arm_ground = fig11.data[1].y;

            let index = Math.floor(pelvis_rotation.length * (currentTime / duration))

            if (index >= pelvis_rotation.length) {
                index = pelvis_rotation.length - 1;
            }

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

            // Sliders
            const slider_pelvis_rot = document.getElementById('slider_pelvis_rot');
            const slider_pelvis_bend = document.getElementById('slider_pelvis_bend');
            const slider_thorax_rot = document.getElementById('slider_thorax_rot');
            const slider_thorax_bend = document.getElementById('slider_thorax_bend');
            const slider_head_rot = document.getElementById('slider_head_rot');
            const slider_head_tilt = document.getElementById('slider_head_tilt');
            const slider_arm_rot = document.getElementById('slider_arm_rot');
            const slider_arm_ground = document.getElementById('slider_arm_ground');

            // Margins
            const margin_pelvis_rot = document.getElementById('pelvis_rot_store').innerHTML.split(', ')
            const margin_pelvis_bend = document.getElementById('pelvis_bend_store').innerHTML.split(', ')
            const margin_thorax_rot = document.getElementById('thorax_rot_store').innerHTML.split(', ')
            const margin_thorax_bend = document.getElementById('thorax_bend_store').innerHTML.split(', ')
            const margin_head_rot = document.getElementById('head_rot_store').innerHTML.split(', ')
            const margin_head_tilt = document.getElementById('head_tilt_store').innerHTML.split(', ')

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
                pelvis_rot_div.style.color = ((value_pelvis_rotation < margin_pelvis_rot[4]) || (value_pelvis_rotation > margin_pelvis_rot[5])) ? 'red' : 'green';
                pelvis_bend_div.style.color = ((value_pelvis_bend < margin_pelvis_bend[4]) || (value_pelvis_bend > margin_pelvis_bend[5])) ? 'red' : 'green';
                thorax_rot_div.style.color = ((value_thorax_rotation < margin_thorax_rot[4]) || (value_thorax_rotation > margin_thorax_rot[5])) ? 'red' : 'green';
                thorax_bend_div.style.color = ((value_thorax_bend < margin_thorax_bend[4]) || (value_thorax_bend > margin_thorax_bend[5])) ? 'red' : 'green';
                head_rot_div.style.color = ((value_head_rotation < margin_head_rot[4]) || (value_head_rotation > margin_head_rot[5])) ? 'red' : 'green';
                head_tilt_div.style.color = ((value_head_tilt < margin_head_tilt[4]) || (value_head_tilt > margin_head_tilt[5])) ? 'red' : 'green';

            }
            else if (button_recent_name === 'top') {
                pelvis_rot_div.style.color = ((value_pelvis_rotation < margin_pelvis_rot[2]) || (value_pelvis_rotation > margin_pelvis_rot[3])) ? 'red' : 'green';
                pelvis_bend_div.style.color = ((value_pelvis_bend < margin_pelvis_bend[2]) || (value_pelvis_bend > margin_pelvis_bend[3])) ? 'red' : 'green';
                thorax_rot_div.style.color = ((value_thorax_rotation < margin_thorax_rot[2]) || (value_thorax_rotation > margin_thorax_rot[3])) ? 'red' : 'green';
                thorax_bend_div.style.color = ((value_thorax_bend < margin_thorax_bend[2]) || (value_thorax_bend > margin_thorax_bend[3])) ? 'red' : 'green';
                head_rot_div.style.color = ((value_head_rotation < margin_head_rot[2]) || (value_head_rotation > margin_head_rot[3])) ? 'red' : 'green';
                head_tilt_div.style.color = ((value_head_tilt < margin_head_tilt[2]) || (value_head_tilt > margin_head_tilt[3])) ? 'red' : 'green';

            }
            else if (button_recent_name === 'setup') {
                pelvis_rot_div.style.color = ((value_pelvis_rotation < margin_pelvis_rot[0]) || (value_pelvis_rotation > margin_pelvis_rot[1])) ? 'red' : 'green';
                pelvis_bend_div.style.color = ((value_pelvis_bend < margin_pelvis_bend[0]) || (value_pelvis_bend > margin_pelvis_bend[1])) ? 'red' : 'green';
                thorax_rot_div.style.color = ((value_thorax_rotation < margin_thorax_rot[0]) || (value_thorax_rotation > margin_thorax_rot[1])) ? 'red' : 'green';
                thorax_bend_div.style.color = ((value_thorax_bend < margin_thorax_bend[0]) || (value_thorax_bend > margin_thorax_bend[1])) ? 'red' : 'green';
                head_rot_div.style.color = ((value_head_rotation < margin_head_rot[0]) || (value_head_rotation > margin_head_rot[1])) ? 'red' : 'green';
                head_tilt_div.style.color = ((value_head_tilt < margin_head_tilt[0]) || (value_head_tilt > margin_head_tilt[1])) ? 'red' : 'green';

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

        showNavbar: function(n_clicks, header_clicks, mobile_clicks, sidebar_class, navbar_main_class) {
            if (window.dash_clientside.callback_context.triggered[0].prop_id === 'menu-button.n_clicks') {
                sidebar_class = sidebar_class.replace('hidden', 'flex')
                navbar_main_class = navbar_main_class.replace('hidden', 'lg:hidden')

                return [sidebar_class, navbar_main_class]
            }

            sidebar_class = sidebar_class.replace('flex', 'hidden')
            navbar_main_class = navbar_main_class.replace('lg:hidden', 'hidden')

            return [sidebar_class, navbar_main_class]

        },

        hideSelectionView: function(n_clicks, selection_class) {

            let pelvis_rot_store = document.getElementById('pelvis_rot_store')
            let pelvis_tilt_store = document.getElementById('pelvis_bend_store')
            let thorax_rot_store = document.getElementById('thorax_rot_store')
            let thorax_tilt_store = document.getElementById('thorax_bend_store')
            let head_rot_store = document.getElementById('head_rot_store')
            let head_tilt_store = document.getElementById('head_tilt_store')

            const setup_low = document.getElementById('setup_low_new_margins').value
            const setup_high = document.getElementById('setup_high_new_margins').value
            const top_low = document.getElementById('top_low_new_margins').value
            const top_high = document.getElementById('top_high_new_margins').value
            const impact_low = document.getElementById('impact_low_new_margins').value
            const impact_high = document.getElementById('impact_high_new_margins').value

            const body_part = document.getElementById('new_margins_title').innerHTML
            // console.log(body_part)

            if (body_part.includes('Pelvis Rot')) {
                pelvis_rot_store.innerHTML = setup_low + ', ' + setup_high + ', ' + top_low + ', ' + top_high + ', ' + impact_low + ', ' + impact_high
            }
            else if (body_part.includes('Pelvis Tilt')) {
                pelvis_tilt_store.innerHTML = setup_low + ', ' + setup_high + ', ' + top_low + ', ' + top_high + ', ' + impact_low + ', ' + impact_high
            }
            else if (body_part.includes('Thorax Rot')) {
                thorax_rot_store.innerHTML = setup_low + ', ' + setup_high + ', ' + top_low + ', ' + top_high + ', ' + impact_low + ', ' + impact_high
            }
            else if (body_part.includes('Thorax Tilt')) {
                thorax_tilt_store.innerHTML = setup_low + ', ' + setup_high + ', ' + top_low + ', ' + top_high + ', ' + impact_low + ', ' + impact_high
            }
            else if (body_part.includes('Head Rot')) {
                head_rot_store.innerHTML = setup_low + ', ' + setup_high + ', ' + top_low + ', ' + top_high + ', ' + impact_low + ', ' + impact_high
            }
            else if (body_part.includes('Head Tilt')) {
                head_tilt_store.innerHTML = setup_low + ', ' + setup_high + ', ' + top_low + ', ' + top_high + ', ' + impact_low + ', ' + impact_high
            }
            else {
                console.log('No body part selected')
            }

            return selection_class.replace('flex', 'hidden');

        },

        showSelectionView: function(n_clicks, n_clicks2, n_clicks3, n_clicks4, n_clicks5, n_clicks6, selection_class) {

                const title = document.getElementById('new_margins_title');
                let selection_view_dismiss = document.getElementById('selection-view-dismiss').classList
                selection_view_dismiss.toggle('hidden')

                // let setup_low = document.getElementById('setup_low_new_margins')
                // let setup_high = document.getElementById('setup_high_new_margins')
                // let top_low = document.getElementById('top_low_new_margins')
                // let top_high = document.getElementById('top_high_new_margins')
                // let impact_low = document.getElementById('impact_low_new_margins')
                // let impact_high = document.getElementById('impact_high_new_margins')
                let setup_low = 0
                let setup_high = 0
                let top_low = 0
                let top_high = 0
                let impact_low = 0
                let impact_high = 0

                if (window.dash_clientside.callback_context.triggered[0].prop_id === 'pelvis_rot_btn.n_clicks') {
                    const pelvis_rot_store = document.getElementById('pelvis_rot_store').innerHTML
                    // console.log(pelvis_rot_store)
                    const pelvis_rot = pelvis_rot_store.split(', ')

                    // Default values for input fields
                    setup_low = pelvis_rot[0]
                    setup_high = pelvis_rot[1]
                    top_low = pelvis_rot[2]
                    top_high = pelvis_rot[3]
                    impact_low = pelvis_rot[4]
                    impact_high = pelvis_rot[5]

                    title.innerHTML = 'New Margins for Pelvis Rotation';
                }

                else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'pelvis_tilt_btn.n_clicks') {
                    const pelvis_tilt_store = document.getElementById('pelvis_bend_store').innerHTML
                    const pelvis_tilt = pelvis_tilt_store.split(', ')

                    setup_low = pelvis_tilt[0]
                    setup_high = pelvis_tilt[1]
                    top_low = pelvis_tilt[2]
                    top_high = pelvis_tilt[3]
                    impact_low = pelvis_tilt[4]
                    impact_high = pelvis_tilt[5]

                    title.innerHTML = 'New Margins for Pelvis Tilt';
                }

                else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'thorax_rot_btn.n_clicks') {
                    const thorax_rot_store = document.getElementById('thorax_rot_store').innerHTML
                    const thorax_rot = thorax_rot_store.split(', ')

                    setup_low = thorax_rot[0]
                    setup_high = thorax_rot[1]
                    top_low = thorax_rot[2]
                    top_high = thorax_rot[3]
                    impact_low = thorax_rot[4]
                    impact_high = thorax_rot[5]

                    title.innerHTML = 'New Margins for Thorax Rotation';
                }

                else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'thorax_tilt_btn.n_clicks') {
                    const thorax_tilt_store = document.getElementById('thorax_bend_store').innerHTML
                    const thorax_tilt = thorax_tilt_store.split(', ')

                    setup_low = thorax_tilt[0]
                    setup_high = thorax_tilt[1]
                    top_low = thorax_tilt[2]
                    top_high = thorax_tilt[3]
                    impact_low = thorax_tilt[4]
                    impact_high = thorax_tilt[5]

                    title.innerHTML = 'New Margins for Thorax Bend';
                }

                else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'head_rot_btn.n_clicks') {
                    const head_rot_store = document.getElementById('head_rot_store').innerHTML
                    const head_rot = head_rot_store.split(', ')

                    setup_low = head_rot[0]
                    setup_high = head_rot[1]
                    top_low = head_rot[2]
                    top_high = head_rot[3]
                    impact_low = head_rot[4]
                    impact_high = head_rot[5]

                    title.innerHTML = 'New Margins for Head Rotation';
                }

                else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'head_tilt_btn.n_clicks') {
                    const head_tilt_store = document.getElementById('head_tilt_store').innerHTML
                    const head_tilt = head_tilt_store.split(', ')

                    setup_low = head_tilt[0]
                    setup_high = head_tilt[1]
                    top_low = head_tilt[2]
                    top_high = head_tilt[3]
                    impact_low = head_tilt[4]
                    impact_high = head_tilt[5]

                    title.innerHTML = 'New Margins for Head Tilt';
                }

                else {
                    title.innerHTML = 'New Margins';
                }

                selection_class = selection_class.replace('hidden', 'flex');



                return [selection_class, setup_low, setup_high, top_low, top_high, impact_low, impact_high];

        },

        hideSelectionViewCross: function(n_clicks, n_clicks2, selection_class, dismiss_class) {
            let selection_view_dismiss = document.getElementById('selection-view-dismiss').classList
            selection_view_dismiss.toggle('hidden')
            return selection_class.replace('flex', 'hidden');
        },

        tempoSlider: function(tempo) {
            return {'left': tempo/6 * 100 + '%'}
        },

        backswingSlider: function(backswing) {
            backswing = Number(backswing.split(' ')[0])
            return {'left': backswing/1.5 * 100 + '%'}
        },

        downswingSlider: function(downswing) {
            downswing = Number(downswing.split(' ')[0])
            return {'left': downswing/0.5 * 100 + '%'}
        },

        toggleHeart: function(n_clicks, url) {
            if (n_clicks > 0) {
                let file = url.split('/')[3];
                let heart = document.getElementById('heart');
                let heart_navbar = document.getElementById(`heart_${file}`);
                heart.classList.toggle('is-active');
                heart_navbar.classList.toggle('is-active');
            }
        },

        toggleDeleteView: function(n_clicks) {
            if (n_clicks > 0) {
                // console.log(n_clicks)
                let delete_view = document.getElementById('delete-file-view').classList
                delete_view.toggle('hidden')

                return 0

            }
        },

        hideDeleteView: function(n_clicks, n_clicks2) {
            if ((n_clicks !== null) || (n_clicks2 !== null)) {
                let delete_view = document.getElementById('delete-file-view').classList
                delete_view.toggle('hidden')
            }
        },

        deleteViewFile: function(n_clicks) {
                if (n_clicks !== null) {
                    let button = window.dash_clientside.callback_context.triggered[0].prop_id
                    button = button.split('.')[0]
                    button = JSON.parse(button)
                    button = button['index']
                    return  button
                }
        },

        showEditPositionsSaveButton: function(n_clicks, n_clicks2, n_clicks3) {
            if (n_clicks > 0 || n_clicks2 > 0 || n_clicks3 > 0) {
                let button = document.getElementById('edit_positions_div').classList
                button.toggle('hidden')
            }
        },

        showOverlay: function(n_clicks, n_clicks2, n_clicks3) {
            if (n_clicks > 0 || n_clicks2 > 0 || n_clicks3 > 0) {
                let overlay = document.getElementById('overlay').classList
                overlay.toggle('hidden')

                let main_wrapper = document.getElementById('main_wrapper').classList
                main_wrapper.toggle('overflow-hidden')

                let body = document.getElementById('body').classList
                body.toggle('overflow-hidden')

            }
        },

        showVideoFrames: function (n_clicks, setup, impact, top) {
            if (n_clicks === 1) {
                let video = document.getElementById('video').children[0]
                var canvas = document.getElementById("setup_frame");

                var canvas_impact = document.getElementById("impact_frame");

                var canvas_top = document.getElementById("top_frame");

                const duration = video.duration;

                console.log(setup)

                // Take the first snapshot
                takeSnapshot(video, canvas, setup * duration).then(function() {
                  // Wait for the first snapshot to finish loading before taking the second one
                  return takeSnapshot(video, canvas_top, top * duration);
                }).then(function() {
                  // Wait for the second snapshot to finish loading before taking the third one
                  return takeSnapshot(video, canvas_impact, impact * duration);
                }).then(function() {
                  // All snapshots have finished loading
                  // console.log("All snapshots taken");
                }).catch(function(error) {
                  // Handle any errors that may occur
                  console.error(error);
                });

            }
        },

        reportText: function (n_clicks, fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10, fig11, setup, impact, top) {
            if (n_clicks === 1) {
                const pelvis_rotation = fig2.data[1].y;
                const pelvis_bend = fig2.data[0].y;
                const thorax_rotation = fig4.data[0].y;
                const thorax_bend = fig4.data[1].y;
                const head_tilt = fig7.data[0].y;
                const head_rotation = fig8.data[0].y;
                const arm_rotation = fig11.data[0].y;
                const arm_ground = fig11.data[1].y;

                setup = Number(setup)
                impact = Number(impact)
                top = Number(top)

                const length = pelvis_rotation.length;

                const pelvis_rot_margins = document.getElementById('pelvis_rot_store').innerHTML.split(', ');
                const thorax_rot_margins = document.getElementById('thorax_rot_store').innerHTML.split(', ');
                const head_rot_margins = document.getElementById('head_rot_store').innerHTML.split(', ');

                const pelvis_rot = pelvis_rotation[Math.floor(setup * length)];
                const thorax_rot = thorax_rotation[Math.floor(setup * length)];
                const head_rot = head_rotation[Math.floor(setup * length)];

                const pelvis_rot_top = pelvis_rotation[Math.floor(top * length)];
                const thorax_rot_top = thorax_rotation[Math.floor(top * length)];
                const head_rot_top = head_rotation[Math.floor(top * length)];

                let pelvis_report_text = document.getElementById('pelvis_report_text');
                let thorax_report_text = document.getElementById('thorax_report_text');
                let head_report_text = document.getElementById('head_report_text');

                let pelvis_report_text_top = document.getElementById('pelvis_report_text_top');
                let thorax_report_text_top = document.getElementById('thorax_report_text_top');
                let head_report_text_top = document.getElementById('head_report_text_top');

                rotationText(pelvis_rot, pelvis_rot_margins, 'pelvis', pelvis_report_text)
                rotationText(thorax_rot, thorax_rot_margins, 'thorax', thorax_report_text)
                rotationText(head_rot, head_rot_margins, 'head', head_report_text)

                rotationText(pelvis_rot_top, pelvis_rot_margins.slice(2, 4), 'pelvis', pelvis_report_text_top)
                rotationText(thorax_rot_top, thorax_rot_margins.slice(2, 4), 'thorax', thorax_report_text_top)
                rotationText(head_rot_top, head_rot_margins.slice(2, 4), 'head', head_report_text_top)

            }
        }

    }
});


// Define the takeSnapshot function
function takeSnapshot(video, canvas, time) {
  return new Promise(function(resolve, reject) {
    var ctx = canvas.getContext("2d");

    // Calculate the aspect ratio of the video
    var aspectRatio = video.videoWidth / video.videoHeight;

    const maxWidth = 384;
    const maxHeight = 384;

    // Calculate the maximum width and height of the canvas based on the aspect ratio
    var canvasWidth, canvasHeight;
    if (aspectRatio > 1) {
        canvasWidth = Math.min(maxWidth, video.videoWidth);
        canvasHeight = canvasWidth / aspectRatio;
    } else {
        canvasHeight = Math.min(maxHeight, video.videoHeight);
        canvasWidth = canvasHeight * aspectRatio;
    }

    // Set the width and height of the canvas
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;

    // Create a closure to capture the current time value
    function captureSnapshot() {
      // Draw the frame onto the canvas
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Remove the event listener
      video.removeEventListener("seeked", captureSnapshot);

      // Resolve the promise
      resolve();
    }

    // Seek to the desired time
    video.currentTime = time;

    // Wait for the video to load that specific frame
    video.addEventListener("seeked", captureSnapshot, false);
  });
}

function rotationText(angle, margin, body_part, element) {
    if (angle < margin[0]) {
        element.innerHTML =  `Rotate your ${body_part} a little less.`
    }
    else if (angle > margin[1]) {
        element.innerHTML = `Rotate your ${body_part} a little more.`
    }
    else {
        element.innerHTML = `Your ${body_part} rotation is good.`
    }
}
