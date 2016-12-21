package com.saidalattrach.friendlocation;

import android.app.Activity;
import android.location.Location;
import android.os.Bundle;
import android.widget.TextView;

import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.api.GoogleApiClient;

import com.google.android.gms.location.LocationServices;;

public class MainActivity extends Activity implements GoogleApiClient.ConnectionCallbacks,
        GoogleApiClient.OnConnectionFailedListener
{
    GoogleApiClient client;
    TextView textView;

    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        textView = (TextView) findViewById(R.id.text_view);

        client = new GoogleApiClient.Builder(this)
                .addConnectionCallbacks(this)
                .addOnConnectionFailedListener(this)
                .addApi(LocationServices.API)
                .build();
    }

    protected void onStart()
    {
        super.onStart();
        client.connect();
    }

    protected void onStop()
    {
        super.onStop();
        client.disconnect();
    }

    public void onConnected(Bundle bundle)
    {
        try
        {
            Location location = null;
            location = LocationServices.FusedLocationApi.getLastLocation(client);
            if (location != null)
                textView.setText("Longitude: " + location.getLongitude()
                        + ", latitude: " + location.getLatitude());
        }
        catch (SecurityException ignored) {}
    }

    public void onConnectionSuspended(int i) {}

    public void onConnectionFailed(ConnectionResult connectionResult) {}
}
