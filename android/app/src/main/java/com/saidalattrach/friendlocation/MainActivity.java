package com.saidalattrach.friendlocation;

import android.app.Activity;

import android.content.ComponentName;
import android.content.Intent;
import android.content.IntentSender;
import android.content.ServiceConnection;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.IBinder;

import android.view.KeyEvent;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.NumberPicker;

import android.support.v7.widget.SwitchCompat;
import android.widget.TextView;

import com.google.android.gms.common.api.Status;

public class MainActivity extends Activity
{
    private static final int SETTINGS_REQUEST_CODE = 1;

    private static final int MIN_UPDATE_INTERVAL = 1;
    private static final int MAX_UPDATE_INTERVAL = 120;
    private static final int DEFAULT_UPDATE_INTERVAL = 30;

    private int updateInterval = DEFAULT_UPDATE_INTERVAL;
    private String username = "";
    private String ipAddress = "";

    private SwitchCompat enableToggle;

    private NumberPicker picker;
    private EditText ipAddressView;
    private EditText usernameView;

    private boolean isServiceBound = false;
    private Intent serviceIntent;
    private ServiceConnection serviceConnection;
    private MainService.LocalBinder localBinder;

    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);

        SharedPreferences preferences = getSharedPreferences("preferences", 0);
        boolean updateLocation = preferences.getBoolean("update_location", false);
        updateInterval = preferences.getInt("update_interval", DEFAULT_UPDATE_INTERVAL);
        ipAddress = preferences.getString("ip_address", "");
        username = preferences.getString("username", "");

        setContentView(R.layout.activity_main);

        enableToggle = (SwitchCompat) findViewById(R.id.enable_update);
        enableToggle.setOnCheckedChangeListener((CompoundButton buttonView, boolean isChecked) ->
        {
            if (isChecked)
            {
                preferences.edit().putBoolean("update_location", true).apply();
                startMainService();
            }
            else
            {
                preferences.edit().putBoolean("update_location", false).apply();
                stopMainService();
            }
        });

        picker = (NumberPicker) findViewById(R.id.update_interval_picker);
        picker.setMinValue(MIN_UPDATE_INTERVAL);
        picker.setMaxValue(MAX_UPDATE_INTERVAL);
        picker.setValue(updateInterval);
        picker.setOnValueChangedListener((NumberPicker p, int oldVal, int newVal) ->
        {
            updateInterval = newVal;
            preferences.edit().putInt("update_interval", updateInterval).apply();
        });

        ipAddressView = (EditText) findViewById(R.id.ip_address);
        ipAddressView.setText(ipAddress);
        ipAddressView.setOnEditorActionListener((TextView v, int actionId, KeyEvent event) ->
                {
                    ipAddress = v.getText().toString();
                    preferences.edit().putString("ip_address", ipAddress).apply();
                    return true;
                }
        );

        usernameView = (EditText) findViewById(R.id.username);
        usernameView.setText(username);
        usernameView.setOnEditorActionListener((TextView v, int actionId, KeyEvent event) ->
                {
                    username = v.getText().toString();
                    preferences.edit().putString("username", username).apply();
                    return true;
                }
        );

        serviceIntent = new Intent(this, MainService.class);

        serviceConnection = new ServiceConnection()
        {
            public void onServiceConnected(ComponentName name, IBinder binder)
            {
                isServiceBound = true;
                localBinder = (MainService.LocalBinder) binder;
                localBinder.getStatus((Status status) ->
                {
                    if (!status.isSuccess() && status.hasResolution())
                    {
                        try
                        {
                            status.startResolutionForResult(MainActivity.this, SETTINGS_REQUEST_CODE);
                        } catch (IntentSender.SendIntentException ignored) {}
                    }
                });
            }

            public void onServiceDisconnected(ComponentName name)
            {
                isServiceBound = false;
            }
        };

        enableToggle.setChecked(updateLocation);
    }

    protected void onStart()
    {
        super.onStart();
        bindMainService();
    }

    protected void onStop()
    {
        super.onStop();
        unbindMainService();
    }

    private void enableViews()
    {
        picker.setEnabled(true);
        ipAddressView.setEnabled(true);
        usernameView.setEnabled(true);
    }

    private void disableViews()
    {
        picker.setEnabled(false);
        ipAddressView.setEnabled(false);
        usernameView.setEnabled(false);
    }

    private void startMainService()
    {
        disableViews();
        serviceIntent.putExtra("update_interval", updateInterval);
        serviceIntent.putExtra("ip_address", ipAddress);
        serviceIntent.putExtra("username", username);
        startService(serviceIntent);
        bindMainService();
    }

    private void stopMainService()
    {
        enableViews();
        unbindMainService();
        stopService(serviceIntent);
    }

    private void bindMainService()
    {
        bindService(serviceIntent, serviceConnection, 0);
    }

    private void unbindMainService()
    {
        if (isServiceBound)
        {
            unbindService(serviceConnection);
            isServiceBound = false;
        }
    }

    protected void onActivityResult(int requestCode, int resultCode, Intent data)
    {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == SETTINGS_REQUEST_CODE)
        {
            if (resultCode == RESULT_OK)
                startMainService();
            else
                enableToggle.setChecked(false);
        }
    }
}
