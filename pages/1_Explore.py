import streamlit as st
from utils.data_utils import get_competitors, load_competitor_data
import pandas as pd
import plotly.express as px
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Explore Competitors", 
    page_icon="🔍",
    layout="wide"
)

st.title("Explore Competitor Reviews")

# Get competitors list
competitors = get_competitors()
logger.info(f"Retrieved {len(competitors)} competitors")

if not competitors:
    logger.warning("No competitor data available")
    st.info("No competitor data available. Add competitors using the 'Add Competitors' page.")
else:
    # Competitor selection
    selected_competitors = st.multiselect("Select Competitors", competitors)
    logger.info(f"Selected competitors: {selected_competitors}")
    
    if selected_competitors:
        # Create a container for all competitor data
        all_data = []
        
        for competitor in selected_competitors:
            logger.info(f"Loading data for competitor: {competitor}")
            df = load_competitor_data(competitor)
            if df is not None:
                df['competitor'] = competitor  # Add competitor column
                all_data.append(df)
                logger.info(f"Loaded {len(df)} reviews for {competitor}")
            else:
                logger.error(f"Failed to load data for {competitor}")
        
        if all_data:
            # Combine all competitor data
            combined_df = pd.concat(all_data, ignore_index=True)
            logger.info(f"Combined data shape: {combined_df.shape}")
            
            # Convert date column to datetime if not already
            combined_df['date'] = pd.to_datetime(combined_df['date'])
            
            # Add tag filtering if tag columns exist
            if all(col in combined_df.columns for col in ['shape_tags', 'style_tags', 'type_tags']):
                # Create three columns for tag filters
                filter_col1, filter_col2, filter_col3 = st.columns(3)
                
                with filter_col1:
                    # Get unique shape tags
                    all_shapes = set()
                    for shapes in combined_df['shape_tags'].dropna():
                        if isinstance(shapes, str):
                            shapes = eval(shapes)
                        all_shapes.update(shapes)
                    selected_shapes = st.multiselect("Filter by Shape", sorted(list(all_shapes)))
                
                with filter_col2:
                    # Get unique style tags
                    all_styles = set()
                    for styles in combined_df['style_tags'].dropna():
                        if isinstance(styles, str):
                            styles = eval(styles)
                        all_styles.update(styles)
                    selected_styles = st.multiselect("Filter by Style", sorted(list(all_styles)))
                
                with filter_col3:
                    # Get unique type tags
                    all_types = set()
                    for types in combined_df['type_tags'].dropna():
                        if isinstance(types, str):
                            types = eval(types)
                        all_types.update(types)
                    selected_types = st.multiselect("Filter by Type", sorted(list(all_types)))
                
                # Apply tag filters
                if selected_shapes or selected_styles or selected_types:
                    logger.info(f"Applying tag filters - Shapes: {selected_shapes}, Styles: {selected_styles}, Types: {selected_types}")
                    mask = pd.Series(True, index=combined_df.index)
                    
                    if selected_shapes:
                        shape_mask = combined_df['shape_tags'].apply(
                            lambda x: any(shape in (eval(x) if isinstance(x, str) else (x if isinstance(x, list) else [])) 
                                        for shape in selected_shapes) if pd.notna(x) else False
                        )
                        mask &= shape_mask
                    
                    if selected_styles:
                        style_mask = combined_df['style_tags'].apply(
                            lambda x: any(style in (eval(x) if isinstance(x, str) else (x if isinstance(x, list) else [])) 
                                        for style in selected_styles) if pd.notna(x) else False
                        )
                        mask &= style_mask
                    
                    if selected_types:
                        type_mask = combined_df['type_tags'].apply(
                            lambda x: any(type_tag in (eval(x) if isinstance(x, str) else (x if isinstance(x, list) else [])) 
                                        for type_tag in selected_types) if pd.notna(x) else False
                        )
                        mask &= type_mask
                    
                    combined_df = combined_df[mask]
                    logger.info(f"Data shape after tag filtering: {combined_df.shape}")
            
            # Date range selector
            min_date = combined_df['date'].min()
            max_date = combined_df['date'].max()

            logger.info(f"Min date: {min_date}, Max date: {max_date}")
            logger.info(f"Min date type: {type(min_date)}, Max date type: {type(max_date)}")
            
            # Calculate default date range (last 4 months)
            default_end_date = max_date
            default_start_date = max_date - pd.DateOffset(months=4)
            
            # Ensure default_start_date is not before min_date
            if default_start_date < min_date:
                default_start_date = min_date
            
            date_range = st.date_input(
                "Select Date Range",
                value=(default_start_date.date(), default_end_date.date()),
                min_value=min_date,
                max_value=max_date
            )
            
            # Filter data based on date range
            if len(date_range) == 2:
                start_date, end_date = date_range
                mask = (combined_df['date'].dt.date >= start_date) & (combined_df['date'].dt.date <= end_date)
                filtered_df = combined_df[mask]
                logger.info(f"Filtered data shape after date range: {filtered_df.shape}")
            else:
                filtered_df = combined_df
            
            # Display most recent date and total reviews
            most_recent = filtered_df['date'].max().strftime('%Y-%m-%d')
            st.write(f"Most recent review date: {most_recent}")
            st.write(f"Total reviews: {len(filtered_df)}")
            
            # Create monthly review count chart with competitor breakdown
            monthly_reviews = filtered_df.groupby([filtered_df['date'].dt.strftime('%Y-%m'), 'competitor']).size().reset_index(name='count')
            monthly_reviews.columns = ['month', 'competitor', 'count']
            
            fig = px.bar(
                monthly_reviews,
                x='month',
                y='count',
                color='competitor',
                title='Monthly Review Count by Competitor',
                labels={'month': 'Month', 'count': 'Number of Reviews', 'competitor': 'Competitor'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show top 10 products
            st.subheader("Top 10 Products by Review Count")
            top_products = filtered_df['listing_title'].value_counts().head(10).reset_index()
            top_products.columns = ['Product', 'Review Count']
            
            # Get the corresponding URLs for top products
            top_products['URL'] = top_products['Product'].apply(
                lambda x: filtered_df[filtered_df['listing_title'] == x]['listing_url'].iloc[0]
            )
            
            # Create clickable links
            top_products['Visit'] = top_products.apply(
                lambda x: f'<a href="{x["URL"]}" target="_blank">Visit Product</a>', 
                axis=1
            )
            
            # Display the table with clickable links
            st.write(top_products[['Product', 'Review Count', 'Visit']].to_html(escape=False), unsafe_allow_html=True)
            
            # Show reviews table
            st.subheader("All Reviews")
            # Define base columns
            base_columns = ['date', 'listing_title', 'review_text', 'rating']
            # Add additional columns if they exist
            additional_columns = ['shape_tags', 'style_tags', 'type_tags']
            columns_to_show = base_columns + [col for col in additional_columns if col in filtered_df.columns]
            
            reviews_table = filtered_df[columns_to_show].sort_values('date', ascending=False)
            # Create column names mapping
            column_names = {
                'date': 'Date',
                'listing_title': 'Product',
                'review_text': 'Review',
                'rating': 'Rating',
                'shape_tags': 'Shape',
                'style_tags': 'Style',
                'type_tags': 'Type'
            }
            reviews_table.columns = [column_names[col] for col in columns_to_show]
            st.dataframe(reviews_table, use_container_width=True)

            # Add Tag Explore section only if tag columns exist
            if all(col in filtered_df.columns for col in ['shape_tags', 'style_tags', 'type_tags']):
                st.subheader("Tag Explore")
                
                # Get unique listings
                unique_listings = filtered_df.drop_duplicates(subset=['listing_title'])
                
                # Function to count tags
                def count_tags(tag_list):
                    if isinstance(tag_list, str):
                        # Convert string representation of list to actual list
                        tag_list = eval(tag_list)
                    if not isinstance(tag_list, list):
                        return {}
                    return {tag: 1 for tag in tag_list}
                
                # Count tags for each category
                shape_counts = {}
                style_counts = {}
                type_counts = {}
                
                for _, row in unique_listings.iterrows():
                    # Count shape tags
                    for shape, count in count_tags(row['shape_tags']).items():
                        shape_counts[shape] = shape_counts.get(shape, 0) + count
                    
                    # Count style tags
                    for style, count in count_tags(row['style_tags']).items():
                        style_counts[style] = style_counts.get(style, 0) + count
                    
                    # Count type tags
                    for type_tag, count in count_tags(row['type_tags']).items():
                        type_counts[type_tag] = type_counts.get(type_tag, 0) + count
                
                # Create three columns for displaying tag counts
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("Shape Tags")
                    shape_df = pd.DataFrame(list(shape_counts.items()), columns=['Shape', 'Count'])
                    shape_df = shape_df.sort_values('Count', ascending=False)
                    st.dataframe(shape_df, use_container_width=True)
                    
                    # Create pie chart for shapes
                    fig_shape = px.pie(shape_df, values='Count', names='Shape', title='Shape Distribution')
                    st.plotly_chart(fig_shape, use_container_width=True)
                
                with col2:
                    st.write("Style Tags")
                    style_df = pd.DataFrame(list(style_counts.items()), columns=['Style', 'Count'])
                    style_df = style_df.sort_values('Count', ascending=False)
                    st.dataframe(style_df, use_container_width=True)
                    
                    # Create pie chart for styles
                    fig_style = px.pie(style_df, values='Count', names='Style', title='Style Distribution')
                    st.plotly_chart(fig_style, use_container_width=True)
                
                with col3:
                    st.write("Type Tags")
                    type_df = pd.DataFrame(list(type_counts.items()), columns=['Type', 'Count'])
                    type_df = type_df.sort_values('Count', ascending=False)
                    st.dataframe(type_df, use_container_width=True)
                    
                    # Create pie chart for types
                    fig_type = px.pie(type_df, values='Count', names='Type', title='Type Distribution')
                    st.plotly_chart(fig_type, use_container_width=True)

        else:
            logger.error(f"Error loading data for {selected_competitors}")
            st.error(f"Error loading data for {selected_competitors}") 